# %% [markdown]
# # Fund-Manager Analytics
#
# A working notebook over the tracker's price history (`data/prices/`) and holdings.
# Open in VS Code / Jupyter (cells are marked with `# %%`) and re-run / tweak freely.
#
# **Stage 1 — Inputs: expected returns (μ) and risk (Σ).**
#
# - **Universe:** your *controllable* positions — direct holdings + the Syfe Core Equity100 fund as a
#   single asset (you trade the fund as a unit; a look-through is used later only for risk attribution).
# - **Window:** last 3 years of daily returns. Assets with too little history (e.g. SpaceX, listed days
#   ago) and cash are **excluded from estimation** but stay in your portfolio.
# - **Choices:** μ = **CAPM-implied** (primary); Σ = **Ledoit-Wolf shrinkage** (primary). Historical &
#   shrunk μ and sample & EWMA Σ are computed alongside for comparison. Benchmark = **ACWI**. r_f = **4%**.

# %%
from __future__ import annotations
import csv
import json
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.covariance import LedoitWolf

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
PRICES = DATA / "prices"
OUT = ROOT / "analytics" / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

# --- config ---
RF_ANNUAL = 0.04          # risk-free rate (annual)
LOOKBACK_YEARS = 3        # estimation window
TRADING_DAYS = 252
BENCHMARK = "ACWI"        # global-equity benchmark
POS_CAP = 0.25            # max weight per position (used in Stage 2)
CRYPTO_CAP = 0.20         # max crypto sleeve (used in Stage 2)
FUND_NAME = "Syfe Core Equity100"
pd.set_option("display.width", 140, "display.max_columns", 20)


# %%
# --- data loading & universe construction ---
def _num(x) -> float:
    try:
        return float(str(x).replace(",", "").replace("$", "").strip())
    except (TypeError, ValueError):
        return 0.0


def price_series(ticker: str):
    p = PRICES / f"{ticker}.csv"
    if not p.exists():
        return None
    return pd.read_csv(p, parse_dates=["date"]).set_index("date")["close"].sort_index()


def build_universe():
    """Price frame + asset->class map + current $ values. Syfe fund = one synthetic asset."""
    holdings = list(csv.DictReader((DATA / "holdings.csv").open()))
    funds = json.loads((DATA / "config.json").read_text()).get("managed_funds", {})
    latest = json.loads((DATA / "latest.json").read_text())
    val = {p["ticker"]: p["value_base"] for p in latest["positions"]}
    fund_val = {f["name"]: f["value"] for f in latest.get("funds", [])}

    series, cls, value = {}, {}, {}
    fund_units = {}
    for h in holdings:
        t = h["ticker"].strip()
        ac = (h.get("asset_class") or "").lower()
        plat = h.get("platform") or ""
        if ac == "cash":
            continue
        if plat in funds:               # Syfe member -> fold into the fund asset
            fund_units[t] = _num(h["quantity"])
            continue
        s = price_series(t)
        if s is None:
            continue
        series[t], cls[t], value[t] = s, ac, val.get(t, 0.0)

    if fund_units:                      # synthetic fund value = sum(units * price)
        fdf = pd.DataFrame({t: price_series(t) * q for t, q in fund_units.items()})
        series[FUND_NAME] = fdf.sum(axis=1, min_count=len(fund_units))
        cls[FUND_NAME] = "fund"
        value[FUND_NAME] = fund_val.get(FUND_NAME, float(series[FUND_NAME].dropna().iloc[-1]))

    return pd.DataFrame(series), cls, value


def returns_window(price_df):
    end = price_df.index.max()
    start = end - pd.Timedelta(days=365 * LOOKBACK_YEARS)
    bdays = pd.bdate_range(price_df.index.min(), end)
    px = price_df.reindex(bdays).ffill()
    win = px.pct_change().loc[start:end]
    full = [c for c in win.columns if win[c].notna().all()]
    dropped = [c for c in win.columns if c not in full]
    return win[full], dropped, (start.date(), end.date())


def benchmark_returns(idx):
    raw = yf.Ticker(BENCHMARK).history(
        start=idx.min() - pd.Timedelta(days=7), end=idx.max() + pd.Timedelta(days=2), auto_adjust=True
    )["Close"]
    raw.index = pd.to_datetime(raw.index).tz_localize(None).normalize()
    s = raw.reindex(pd.bdate_range(raw.index.min(), idx.max())).ffill()
    return s.pct_change().reindex(idx)


price_df, CLS, VALUE = build_universe()
rets, dropped, (win_start, win_end) = returns_window(price_df)
bench = benchmark_returns(rets.index)

print(f"Universe: {rets.shape[1]} assets | window {win_start}..{win_end} | {rets.shape[0]} obs")
print(f"Excluded (insufficient history): {dropped or 'none'}  (+ cash)")


# %%
# --- Stage 1: expected returns (mu) ---
rf_d = RF_ANNUAL / TRADING_DAYS
mkt_ex = bench - rf_d
erp_annual = mkt_ex.mean() * TRADING_DAYS                 # realised market excess return (annualised)
betas = {c: (rets[c] - rf_d).cov(mkt_ex) / mkt_ex.var() for c in rets.columns}

mu_capm = pd.Series({c: RF_ANNUAL + betas[c] * erp_annual for c in rets.columns})
mu_hist = rets.mean() * TRADING_DAYS
mu_shrunk = 0.5 * mu_hist.mean() + 0.5 * mu_hist          # James-Stein-style shrink to grand mean

print(f"Benchmark ({BENCHMARK}): ann. excess return (ERP) = {erp_annual:.1%}, "
      f"ann. vol = {bench.std() * np.sqrt(TRADING_DAYS):.1%}")


# %%
# --- Stage 1: covariance (Sigma) ---
Sigma_sample = rets.cov() * TRADING_DAYS
lw = LedoitWolf().fit(rets.values)
Sigma_lw = pd.DataFrame(lw.covariance_ * TRADING_DAYS, index=rets.columns, columns=rets.columns)
Sigma_ewma = rets.ewm(halflife=60).cov(pairwise=True).xs(rets.index[-1]) * TRADING_DAYS

vol = pd.Series(np.sqrt(np.diag(Sigma_lw)), index=rets.columns)
d = np.sqrt(np.diag(Sigma_lw.values))
corr = pd.DataFrame(Sigma_lw.values / np.outer(d, d), index=rets.columns, columns=rets.columns)

print(f"Ledoit-Wolf shrinkage intensity = {lw.shrinkage_:.2f}  "
      f"(0 = sample cov, 1 = fully shrunk to target)")


# %%
# --- Stage 1 summary table ---
w = pd.Series(VALUE).reindex(rets.columns)
w = w / w.sum()                                          # weights over the estimated universe

summary = pd.DataFrame({
    "class": [CLS[c] for c in rets.columns],
    "weight": w,
    "ann_vol": vol,
    "beta": pd.Series(betas),
    "mu_CAPM": mu_capm,
    "mu_hist": mu_hist,
    "mu_shrunk": mu_shrunk,
}).sort_values("weight", ascending=False)

show = summary.copy()
for col in ["weight", "ann_vol", "mu_CAPM", "mu_hist", "mu_shrunk"]:
    show[col] = (show[col] * 100).round(1).astype(str) + "%"
show["beta"] = show["beta"].round(2)
print("\n=== Stage 1: per-asset inputs (annualised) ===")
print(show.to_string())

summary.to_csv(OUT / "stage1_inputs.csv")
corr.round(3).to_csv(OUT / "correlation.csv")
Sigma_lw.to_csv(OUT / "sigma_ledoitwolf.csv")


# %%
# --- correlation heatmap ---
fig, ax = plt.subplots(figsize=(10, 8))
im = ax.imshow(corr.values, vmin=-1, vmax=1, cmap="RdBu_r")
ax.set_xticks(range(len(corr)), corr.columns, rotation=90, fontsize=8)
ax.set_yticks(range(len(corr)), corr.index, fontsize=8)
for i in range(len(corr)):
    for j in range(len(corr)):
        ax.text(j, i, f"{corr.values[i, j]:.2f}", ha="center", va="center",
                fontsize=6, color="white" if abs(corr.values[i, j]) > 0.55 else "black")
fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label="correlation")
ax.set_title(f"Correlation matrix (Ledoit-Wolf, {win_start}..{win_end})")
fig.tight_layout()
fig.savefig(OUT / "correlation_heatmap.png", dpi=130)
print(f"\nSaved: {OUT/'correlation_heatmap.png'}, stage1_inputs.csv, correlation.csv, sigma_ledoitwolf.csv")


# %% [markdown]
# ## Stage 2 — Mean-variance optimisation
#
# The max-Sharpe (tangency) portfolio, the efficient frontier with your current portfolio on it, and
# min-variance + risk-parity references. Constraints: long-only, fully invested, **≤25% per position,
# ≤20% crypto sleeve**. Inputs: μ = CAPM, Σ = Ledoit-Wolf (from Stage 1).

# %%
from scipy.optimize import minimize

assets = list(rets.columns)
mu_vec = mu_capm.reindex(assets).values
Sig = Sigma_lw.loc[assets, assets].values
n = len(assets)
classes = np.array([CLS[a] for a in assets])
is_crypto = classes == "crypto"
rf = RF_ANNUAL
val = pd.Series(VALUE).reindex(assets)
w_cur = (val / val.sum()).values

def p_ret(w):
    return float(mu_vec @ w)

def p_vol(w):
    return float(np.sqrt(w @ Sig @ w))

def p_sharpe(w):
    return (p_ret(w) - rf) / p_vol(w)

bounds = [(0.0, POS_CAP)] * n
cons_full = [
    {"type": "eq", "fun": lambda w: w.sum() - 1.0},                     # fully invested
    {"type": "ineq", "fun": lambda w: CRYPTO_CAP - w[is_crypto].sum()},  # crypto sleeve cap
]
w0 = np.full(n, 1.0 / n)
OPTS = {"maxiter": 800, "ftol": 1e-11}

w_ms = minimize(lambda w: -p_sharpe(w), w0, method="SLSQP", bounds=bounds, constraints=cons_full, options=OPTS).x
w_mv = minimize(lambda w: w @ Sig @ w, w0, method="SLSQP", bounds=bounds, constraints=cons_full, options=OPTS).x

def rp_obj(w):                                                          # risk parity: equalise risk contributions
    s = np.sqrt(w @ Sig @ w)
    rc = w * (Sig @ w) / s
    return np.sum((rc - rc.mean()) ** 2)

w_rp = minimize(rp_obj, w0, method="SLSQP", bounds=[(0.0, 1.0)] * n,
                constraints=[{"type": "eq", "fun": lambda w: w.sum() - 1.0}], options=OPTS).x

for wv in (w_ms, w_mv, w_rp):
    wv[np.abs(wv) < 1e-5] = 0.0

# %%
# weights comparison + portfolio stats
cmp = pd.DataFrame(
    {"class": classes, "current": w_cur, "max_sharpe": w_ms, "min_var": w_mv, "risk_parity": w_rp},
    index=assets,
).sort_values("current", ascending=False)
print("\n=== Weights: current vs optimised (%) ===")
print(cmp[["class"]].join((cmp[["current", "max_sharpe", "min_var", "risk_parity"]] * 100).round(1)).to_string())

print("\n=== By asset class (%) ===")
print((cmp.groupby("class")[["current", "max_sharpe", "min_var", "risk_parity"]].sum() * 100).round(1).to_string())

rows = {"current": w_cur, "max_sharpe": w_ms, "min_var": w_mv, "risk_parity": w_rp}
stat = pd.DataFrame({k: {"exp_return": p_ret(w), "volatility": p_vol(w), "sharpe": p_sharpe(w)} for k, w in rows.items()}).T
disp = stat.copy()
disp["exp_return"] = (disp["exp_return"] * 100).round(1).astype(str) + "%"
disp["volatility"] = (disp["volatility"] * 100).round(1).astype(str) + "%"
disp["sharpe"] = disp["sharpe"].round(2)
print("\n=== Portfolio stats (annualised) ===")
print(disp.to_string())
print(f"\nSharpe: current {p_sharpe(w_cur):.2f} -> max-Sharpe {p_sharpe(w_ms):.2f} "
      f"(+{p_sharpe(w_ms) - p_sharpe(w_cur):.2f})")
cmp.to_csv(OUT / "stage2_weights.csv")

# %%
# efficient frontier + chart
w_maxret = minimize(lambda w: -p_ret(w), w0, method="SLSQP", bounds=bounds, constraints=cons_full, options=OPTS).x
fr_v, fr_r = [], []
for t in np.linspace(p_ret(w_mv), p_ret(w_maxret), 40):
    cons = cons_full + [{"type": "eq", "fun": lambda w, t=t: p_ret(w) - t}]
    r = minimize(lambda w: w @ Sig @ w, w0, method="SLSQP", bounds=bounds, constraints=cons, options=OPTS)
    if r.success:
        fr_v.append(p_vol(r.x) * 100)
        fr_r.append(t * 100)

fig, ax = plt.subplots(figsize=(9, 6))
ax.plot(fr_v, fr_r, "-", color="#64748b", lw=1.6, label="Efficient frontier")
ax.scatter(np.sqrt(np.diag(Sig)) * 100, mu_vec * 100, s=16, color="#94a3b8", alpha=0.6)
for i, a in enumerate(assets):
    ax.annotate(a[:7], (np.sqrt(Sig[i, i]) * 100, mu_vec[i] * 100), fontsize=6, color="#94a3b8")
xs = np.linspace(0, max(fr_v) * 1.05, 50)
ax.plot(xs, rf * 100 + p_sharpe(w_ms) * xs, "--", color="#34d399", lw=1, label="Capital market line")
for name, w, c, m in [("Current", w_cur, "#f87171", "o"), ("Max-Sharpe", w_ms, "#34d399", "*"),
                      ("Min-variance", w_mv, "#60a5fa", "s"), ("Risk-parity", w_rp, "#fbbf24", "D")]:
    ax.scatter(p_vol(w) * 100, p_ret(w) * 100, s=200 if m == "*" else 80, color=c, marker=m,
               label=name, zorder=5, edgecolors="white", linewidths=0.6)
ax.set_xlabel("Volatility (annualised, %)")
ax.set_ylabel("Expected return (annualised, %)")
ax.set_title("Efficient frontier — current vs optimised")
ax.legend(loc="lower right", fontsize=9)
ax.grid(alpha=0.15)
fig.tight_layout()
fig.savefig(OUT / "efficient_frontier.png", dpi=130)
print(f"\nSaved: {OUT/'efficient_frontier.png'}, stage2_weights.csv")
