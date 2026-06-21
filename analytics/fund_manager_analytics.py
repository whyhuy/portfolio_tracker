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


# %% [markdown]
# ## Stage 3 — Risk decomposition: add / trim
#
# At your **current** weights, decompose total risk. For each position:
# **MCR** (marginal contribution to risk = how much portfolio vol moves if you add a sliver), its
# **risk share** (% of total vol it accounts for), its **return share** (% of the portfolio's excess
# return), and its **marginal Sharpe** (excess return ÷ MCR).
#
# **Flag:** ADD if return-share > risk-share, TRIM if it's a risk hog earning too little. This is
# exactly equivalent to "marginal Sharpe above vs below the portfolio Sharpe" — assets above the line
# improve the book at the margin, assets below drag it.

# %%
sig_p = p_vol(w_cur)
mcr = Sig @ w_cur / sig_p                       # marginal contribution to risk
rc = w_cur * mcr                                # risk contribution (sums to sig_p)
risk_share = rc / sig_p                         # % of total risk
exret = mu_vec - rf
ret_share = (w_cur * exret) / (w_cur * exret).sum()
marg_sharpe = exret / mcr                       # marginal Sharpe per position
sharpe_p = p_sharpe(w_cur)

risk3 = pd.DataFrame({
    "class": classes, "weight": w_cur, "risk_share": risk_share,
    "return_share": ret_share, "MCR": mcr, "marg_sharpe": marg_sharpe,
}, index=assets)
risk3["net"] = risk3["return_share"] - risk3["risk_share"]
risk3["flag"] = np.where(risk3["net"] >= 0, "ADD", "TRIM")
risk3 = risk3.sort_values("net", ascending=False)

show3 = risk3.copy()
for c in ["weight", "risk_share", "return_share", "net"]:
    show3[c] = (show3[c] * 100).round(1).astype(str) + "%"
show3["MCR"] = show3["MCR"].round(3)
show3["marg_sharpe"] = show3["marg_sharpe"].round(2)
print(f"Current portfolio: vol {sig_p:.1%} | Sharpe {sharpe_p:.2f}  "
      f"(marginal Sharpe > {sharpe_p:.2f} => ADD at the margin)")
print("\n=== Risk decomposition / add-trim (current weights) ===")
print(show3.to_string())
risk3.to_csv(OUT / "stage3_risk_decomposition.csv")

# %%
order = risk3.sort_values("net")
fig, ax = plt.subplots(figsize=(9, 6))
ax.barh(order.index, order["net"] * 100, color=["#34d399" if v >= 0 else "#f87171" for v in order["net"]])
ax.axvline(0, color="#94a3b8", lw=0.8)
ax.set_xlabel("Return share − risk share (percentage points)    ←  TRIM   |   ADD  →")
ax.set_title("Are you paid for the risk you take? (current weights)")
ax.grid(axis="x", alpha=0.15)
fig.tight_layout()
fig.savefig(OUT / "risk_addtrim.png", dpi=130)
print(f"\nSaved: {OUT/'risk_addtrim.png'}, stage3_risk_decomposition.csv")


# %% [markdown]
# ## Stage 4 — Fund-manager analytics
#
# Risk metrics (VaR / Expected Shortfall, max drawdown / Calmar, Sortino), benchmark-relative stats
# (β, tracking error, information ratio vs ACWI), market-risk-adjusted performance (Treynor, Jensen's
# alpha), up/down capture and hit rate, concentration (HHI + look-through), style-factor
# exposures (factor-ETF proxies for FF5+momentum, aligned to the same window), exposure by region
# (Syfe fund decomposed), stress tests, and a constant-weight backtest of current vs optimised weights.

# %%
# --- portfolio daily returns (current weights, held constant = daily-rebalanced) ---
pr = pd.Series(rets.values @ w_cur, index=rets.index)
ann = TRADING_DAYS
pv = val.sum()                                   # $ value of the analysed universe (ex SpaceX/cash)


def max_drawdown(s):
    cum = (1 + s).cumprod()
    return float((cum / cum.cummax() - 1).min())


cagr = float((1 + pr).prod() ** (ann / len(pr)) - 1)
sd_p = pr.std() * np.sqrt(ann)
downside = pr[pr < 0].std() * np.sqrt(ann)
mdd = max_drawdown(pr)
var95, var99 = -np.percentile(pr, 5), -np.percentile(pr, 1)
es95 = -pr[pr <= np.percentile(pr, 5)].mean()
es99 = -pr[pr <= np.percentile(pr, 1)].mean()

metrics = {
    "Ann. return (CAGR)": cagr, "Ann. volatility": sd_p,
    "Sharpe": (cagr - rf) / sd_p, "Sortino": (cagr - rf) / downside,
    "Max drawdown": mdd, "Calmar": cagr / abs(mdd),
    "VaR 95% (1-day)": var95, "ES 95% (1-day)": es95,
    "VaR 99% (1-day)": var99, "ES 99% (1-day)": es99,
}
print(f"=== Risk metrics — current portfolio, 3y daily (universe ~${pv:,.0f}) ===")
for k, v in metrics.items():
    tail = f"  (~${v * pv:,.0f})" if ("VaR" in k or "ES" in k) else ""
    print(f"  {k:22} {v * 100:7.1f}%{tail}" if "Sharpe" not in k and "Sortino" not in k and "Calmar" not in k
          else f"  {k:22} {v:7.2f}")

# %%
# --- vs benchmark (ACWI) ---
bm = bench.reindex(pr.index)
beta_p = float(np.cov(pr, bm)[0, 1] / bm.var())
active = pr - bm
te = active.std() * np.sqrt(ann)
ir = (active.mean() * ann) / te
print(f"\n=== Vs benchmark (ACWI) ===\n  Beta {beta_p:.2f} | Tracking error {te:.1%} | "
      f"Information ratio {ir:.2f} | ann. active return {active.mean() * ann:+.1%}")

# --- performance ratios: market-risk-adjusted, capture, breadth ---
bm_cagr = float((1 + bm).prod() ** (ann / len(bm)) - 1)        # benchmark annualised return
treynor = (cagr - rf) / beta_p                                 # excess return per unit of MARKET (beta) risk
jensen = cagr - (rf + beta_p * (bm_cagr - rf))                 # CAPM alpha: return above what beta predicts

# up/down capture — compounded over up- vs down-benchmark months (version-agnostic monthly resample)
prm = (1 + pr).groupby(pr.index.to_period("M")).prod() - 1     # portfolio monthly returns
bmm = (1 + bm).groupby(bm.index.to_period("M")).prod() - 1     # benchmark monthly returns
up, dn = bmm > 0, bmm < 0
up_cap = ((1 + prm[up]).prod() - 1) / ((1 + bmm[up]).prod() - 1)
dn_cap = ((1 + prm[dn]).prod() - 1) / ((1 + bmm[dn]).prod() - 1)

# hit rate — breadth of winners across positions, plus share of positive portfolio months
win = (rets + 1).prod() - 1                                    # per-position cumulative return over the window
n_win = int((win > 0).sum())
hit_pos = n_win / len(win)                                     # # winning positions / total positions
hit_mth = float((prm > 0).mean())                             # share of positive portfolio months

print(f"\n=== Performance ratios (market-risk-adjusted, capture, breadth) ===")
print(f"  Treynor ratio        {treynor:6.2f}    (excess return per unit of beta; benchmark ~{bm_cagr - rf:+.1%} per 1.0 beta)")
print(f"  Jensen's alpha       {jensen:+6.1%}    (annualised return above CAPM prediction)")
print(f"  Up-capture           {up_cap:6.0%}    (portfolio vs ACWI in up months;  >100% = amplifies rallies)")
print(f"  Down-capture         {dn_cap:6.0%}    (portfolio vs ACWI in down months; <100% = defensive)")
print(f"  Hit rate (positions) {hit_pos:6.0%}    ({n_win}/{len(win)} positions positive over the window)")
print(f"  Hit rate (months)    {hit_mth:6.0%}    (share of positive portfolio months — consistency)")

# --- concentration (HHI) + look-through ---
latest = json.loads((DATA / "latest.json").read_text())
fund_members = {p["ticker"]: p["value_base"] for p in latest["positions"] if p.get("fund")}
fsum = sum(fund_members.values())
w_lt = {}
for a, wv in zip(assets, w_cur):
    if a == FUND_NAME:
        for t, v in fund_members.items():
            w_lt[t] = w_lt.get(t, 0) + wv * (v / fsum)
    else:
        w_lt[a] = w_lt.get(a, 0) + wv
hhi, hhi_lt = float(np.sum(w_cur ** 2)), float(sum(v ** 2 for v in w_lt.values()))
print(f"\n=== Concentration ===\n  HHI {hhi:.3f} (effective holdings {1/hhi:.1f}) | "
      f"look-through HHI {hhi_lt:.3f} (effective {1/hhi_lt:.1f})")

# %%
# --- style-factor exposures (factor-ETF proxies for FF5 + momentum) ---
def yf_rets(tickers, idx):
    out = {}
    for t in tickers:
        s = yf.Ticker(t).history(start=idx.min() - pd.Timedelta(days=7), end=idx.max() + pd.Timedelta(days=2),
                                 auto_adjust=True)["Close"]
        s.index = pd.to_datetime(s.index).tz_localize(None).normalize()
        out[t] = s.reindex(pd.bdate_range(s.index.min(), idx.max())).ffill().pct_change().reindex(idx)
    return pd.DataFrame(out)


fe = yf_rets(["ACWI", "IWM", "IWB", "IWD", "IWF", "MTUM", "QUAL"], pr.index)
factors = pd.DataFrame({
    "MKT": fe["ACWI"] - rf / ann, "SIZE": fe["IWM"] - fe["IWB"], "VALUE": fe["IWD"] - fe["IWF"],
    "MOM": fe["MTUM"] - fe["IWB"], "QUALITY": fe["QUAL"] - fe["IWB"],
}).dropna()
yv = (pr - rf / ann).reindex(factors.index).values
X = np.column_stack([np.ones(len(factors)), factors.values])
coef, *_ = np.linalg.lstsq(X, yv, rcond=None)
r2 = 1 - (yv - X @ coef).var() / yv.var()
print("\n=== Style-factor exposures (β) ===")
print(f"  alpha {coef[0] * ann:+.1%} (ann.)")
for nm, b in zip(factors.columns, coef[1:]):
    print(f"  {nm:8} {b:+.2f}")
print(f"  R^2 {r2:.2f}")

# %%
# --- exposure by region (look-through on the fund) ---
REGION = {"ORCL": "US", "MSTR": "US", "CEG": "US", "QBTS": "US", "IONQ": "US", "NNDM": "US",
          "ORGN": "US", "MUFG": "Japan", "BZ": "China", "TMC": "Global", "VWO": "EM", "SLV": "Commodity",
          "bitcoin": "Crypto", "ethereum": "Crypto", "crypto-com-chain": "Crypto", "solana": "Crypto",
          "polkadot": "Crypto", "ripple": "Crypto"}
FUND_REGION = {"CSPX.L": "US", "EFA": "DevExUS", "QQQ": "US", "XDEW.L": "US", "DUHP": "US",
               "EIMI.L": "EM", "DFAT": "US", "MOAT": "US", "MCHI": "China", "KWEB": "China"}
reg = {}
for a, wv in zip(assets, w_cur):
    if a == FUND_NAME:
        for t, v in fund_members.items():
            reg[FUND_REGION.get(t, "Other")] = reg.get(FUND_REGION.get(t, "Other"), 0) + wv * (v / fsum)
    else:
        reg[REGION.get(a, "Other")] = reg.get(REGION.get(a, "Other"), 0) + wv
reg = pd.Series(reg).sort_values(ascending=False)
print("\n=== Exposure by region (look-through, %) ===")
print((reg * 100).round(1).to_string())

# %%
# --- stress tests (beta-propagated market shocks + direct crypto shocks) ---
beta_arr = pd.Series(betas).reindex(assets).values
def stress(market=0.0, crypto=0.0):
    pnl = 0.0
    for a, wv, b, cl in zip(assets, w_cur, beta_arr, classes):
        s = (b * market if cl in ("equity", "etf", "fund") else 0.0) + (crypto if cl == "crypto" else 0.0)
        pnl += wv * s
    return pnl
scenarios = {
    "Global equity −20%": dict(market=-0.20),
    "Crypto −50%": dict(crypto=-0.50),
    "Risk-off (eq −15%, crypto −30%)": dict(market=-0.15, crypto=-0.30),
    "Rates +100bps (eq −5%, crypto −10%)": dict(market=-0.05, crypto=-0.10),
}
stress_res = {k: stress(**v) for k, v in scenarios.items()}
print("\n=== Stress tests (portfolio P&L; equity via empirical β) ===")
for k, v in stress_res.items():
    print(f"  {k:36} {v * 100:6.1f}%  (~${v * pv:,.0f})")

# %%
# --- charts: drawdown, stress, backtest ---
cum = (1 + pr).cumprod()
dd = cum / cum.cummax() - 1
fig, ax = plt.subplots(figsize=(9, 3.2))
ax.fill_between(dd.index, dd.values * 100, 0, color="#f87171", alpha=0.5)
ax.set_title(f"Drawdown (underwater) — max {mdd:.0%}")
ax.grid(alpha=0.15)
fig.tight_layout(); fig.savefig(OUT / "drawdown.png", dpi=130)

fig, ax = plt.subplots(figsize=(8, 3.6))
ks = list(stress_res); vs = [stress_res[k] * 100 for k in ks]
ax.barh(ks, vs, color="#f87171")
for i, v in enumerate(vs):
    ax.text(v / 2, i, f"{v:.0f}%  ${stress_res[ks[i]]*pv:,.0f}", va="center", ha="center", color="white", fontsize=8)
ax.axvline(0, color="#94a3b8", lw=0.8); ax.set_title("Stress tests — portfolio P&L"); ax.grid(axis="x", alpha=0.15)
fig.tight_layout(); fig.savefig(OUT / "stress_tests.png", dpi=130)

bt = pd.DataFrame({"Current": rets.values @ w_cur, "Max-Sharpe": rets.values @ w_ms,
                   "Min-variance": rets.values @ w_mv}, index=rets.index)
bt = (1 + bt).cumprod()
fig, ax = plt.subplots(figsize=(9, 5))
for col, c in [("Current", "#f87171"), ("Max-Sharpe", "#34d399"), ("Min-variance", "#60a5fa")]:
    ax.plot(bt.index, bt[col], label=f"{col}  ({(bt[col].iloc[-1]-1)*100:+.0f}%)", color=c, lw=1.6)
ax.set_title("Backtest — constant weights, daily-rebalanced (gross of costs)")
ax.legend(); ax.grid(alpha=0.15)
fig.tight_layout(); fig.savefig(OUT / "backtest.png", dpi=130)
print(f"\nSaved: drawdown.png, stress_tests.png, backtest.png")
print("\n[note] Backtest is constant-weight & gross of costs; real rebalancing to the optimised weights "
      "would incur turnover/transaction costs that shrink the optimised edge. Factors are tradeable-ETF "
      "proxies for FF5+momentum, aligned to the same window.")


# %% [markdown]
# ## Stage 5 — Monte Carlo simulation
#
# 10,000 simulated one-year paths for the portfolio. The **parametric** method draws daily returns as
# geometric Brownian motion from the forward CAPM μ and Ledoit-Wolf Σ; the **bootstrap** method
# resamples actual historical days (keeps fat tails, but replays the bull market). The optimism of the
# whole picture is set by the μ assumption — read it as "given these inputs," not a forecast.

# %%
rng = np.random.default_rng(7)
N_SIMS, H = 10_000, TRADING_DAYS

def mc_gbm(w, n=N_SIMS, h=H):
    mu_a, sig_a = p_ret(w), p_vol(w)
    mu_d, sig_d = mu_a / TRADING_DAYS, sig_a / np.sqrt(TRADING_DAYS)
    logr = rng.normal(mu_d - 0.5 * sig_d ** 2, sig_d, size=(n, h))
    return np.exp(np.cumsum(logr, axis=1))                 # value / start, shape (n, h)

def mc_bootstrap(w, n=N_SIMS, h=H):
    hist = rets.values @ w
    return np.cumprod(1 + hist[rng.integers(0, len(hist), size=(n, h))], axis=1)

def summarise(term, label):
    return {"scenario": label, "median": np.median(term) - 1,
            "p5 (bad)": np.percentile(term, 5) - 1, "p95 (good)": np.percentile(term, 95) - 1,
            "P(loss)": np.mean(term < 1), "P(>+20%)": np.mean(term > 1.2),
            "1y VaR95": 1 - np.percentile(term, 5)}

paths_cur, paths_ms, boot_cur = mc_gbm(w_cur), mc_gbm(w_ms), mc_bootstrap(w_cur)
mc_tab = pd.DataFrame([
    summarise(paths_cur[:, -1], "Current (parametric)"),
    summarise(boot_cur[:, -1], "Current (bootstrap)"),
    summarise(paths_ms[:, -1], "Max-Sharpe (parametric)"),
]).set_index("scenario")
print("=== Monte Carlo — 1-year outcome distribution (10,000 paths) ===")
print(((mc_tab * 100).round(1).astype(str) + "%").to_string())
print(f"\nStart (analysed universe) ~${pv:,.0f} | current 1y median ~${np.median(paths_cur[:,-1])*pv:,.0f}"
      f", bad case (5th pct) ~${np.percentile(paths_cur[:,-1],5)*pv:,.0f}"
      f", good case (95th) ~${np.percentile(paths_cur[:,-1],95)*pv:,.0f}")
mc_tab.to_csv(OUT / "stage5_montecarlo.csv")

# %%
months = np.arange(1, H + 1) / TRADING_DAYS * 12
q = np.percentile(paths_cur, [5, 25, 50, 75, 95], axis=0) * pv
fig, ax = plt.subplots(figsize=(9, 5))
ax.fill_between(months, q[0], q[4], color="#6366f1", alpha=0.15, label="5–95%")
ax.fill_between(months, q[1], q[3], color="#6366f1", alpha=0.30, label="25–75%")
ax.plot(months, q[2], color="#4338ca", lw=2, label="median")
ax.axhline(pv, color="#94a3b8", ls="--", lw=1, label="start")
ax.set_xlabel("months ahead"); ax.set_ylabel("portfolio value ($)")
ax.set_title("Monte Carlo — 10,000 one-year paths (current portfolio)")
ax.legend(loc="upper left"); ax.grid(alpha=0.15)
fig.tight_layout(); fig.savefig(OUT / "montecarlo_fan.png", dpi=130)

# %%
fig, ax = plt.subplots(figsize=(9, 5))
ax.hist((paths_cur[:, -1] - 1) * 100, bins=70, color="#f87171", alpha=0.55, label="Current")
ax.hist((paths_ms[:, -1] - 1) * 100, bins=70, color="#34d399", alpha=0.55, label="Max-Sharpe")
ax.axvline(0, color="#475569", lw=1)
ax.set_xlabel("1-year return (%)"); ax.set_ylabel("number of simulations")
ax.set_title("Distribution of 1-year outcomes — current vs optimised")
ax.legend(); ax.grid(alpha=0.15)
fig.tight_layout(); fig.savefig(OUT / "montecarlo_dist.png", dpi=130)
print("\nSaved: montecarlo_fan.png, montecarlo_dist.png, stage5_montecarlo.csv")
