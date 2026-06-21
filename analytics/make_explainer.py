"""
make_explainer.py
Builds a single self-contained HTML explainer for the fund-manager analytics:
plain-English concepts + maths (MathJax) + the actual charts embedded (base64).
Output -> ../<Personal Finance outputs>/2026-06-20-portfolio-analytics-explainer.html
"""
import base64
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs"
DEST = HERE.parents[1] / "2026-06-20-portfolio-analytics-explainer.html"  # .../Personal Finance/outputs/


def fig(fname, caption):
    data = base64.b64encode((OUT / fname).read_bytes()).decode()
    return (f'<figure><img alt="{caption}" src="data:image/png;base64,{data}">'
            f'<figcaption>{caption}</figcaption></figure>')


CSS = """
:root{--ink:#1a2233;--muted:#5b6677;--line:#e4e8ef;--accent:#3257d6;--bg:#fbfcfe;--box:#f2f5fb;}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
 font:17px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;}
.wrap{max-width:820px;margin:0 auto;padding:48px 22px 120px;}
h1{font-size:2.1rem;line-height:1.2;margin:.2em 0 .1em}
h2{font-size:1.5rem;margin:2.4em 0 .4em;padding-top:.5em;border-top:1px solid var(--line)}
h3{font-size:1.18rem;margin:1.8em 0 .3em;color:#243049}
h4{font-size:1.02rem;margin:1.4em 0 .2em;color:#2c3954}
p,li{color:#222b3d}
a{color:var(--accent)}
.sub{color:var(--muted);font-size:1.05rem;margin-top:0}
.lead{font-size:1.08rem}
code,.num{font-family:"SF Mono",ui-monospace,Menlo,Consolas,monospace;font-size:.92em;
 background:#eef1f7;padding:.05em .35em;border-radius:4px}
figure{margin:1.4em 0;text-align:center}
figure img{max-width:100%;border:1px solid var(--line);border-radius:10px;background:#fff;
 box-shadow:0 2px 10px rgba(20,30,60,.06)}
figcaption{color:var(--muted);font-size:.9rem;margin-top:.5em}
.box{background:var(--box);border:1px solid var(--line);border-left:3px solid var(--accent);
 border-radius:8px;padding:14px 18px;margin:1.2em 0}
.box .h{font-weight:600;font-size:.82rem;letter-spacing:.04em;text-transform:uppercase;
 color:var(--accent);margin-bottom:.3em}
.you{border-left-color:#1f9d63}.you .h{color:#1f9d63}
.warn{border-left-color:#d08400;background:#fdf7ec}.warn .h{color:#b5730a}
table{border-collapse:collapse;width:100%;margin:1.1em 0;font-size:.95rem}
th,td{border-bottom:1px solid var(--line);padding:7px 10px;text-align:right}
th:first-child,td:first-child{text-align:left}
thead th{border-bottom:2px solid #c9d2e3;font-size:.85rem;color:var(--muted)}
.toc{background:#fff;border:1px solid var(--line);border-radius:10px;padding:8px 22px;margin:1.5em 0}
.toc ol{margin:.4em 0;padding-left:1.2em}.toc a{text-decoration:none}
.tag{display:inline-block;background:#eaf0ff;color:var(--accent);border-radius:20px;
 padding:1px 10px;font-size:.78rem;font-weight:600;margin-bottom:8px}
hr{border:none;border-top:1px solid var(--line);margin:2.4em 0}
.small{font-size:.9rem;color:var(--muted)}
"""

HEAD = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Your portfolio analytics, explained</title>
<script>window.MathJax={tex:{inlineMath:[['\\\\(','\\\\)']],displayMath:[['\\\\[','\\\\]']]}};</script>
<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
<style>""" + CSS + """</style></head><body><div class="wrap">"""

FOOT = """<hr><p class="small">Generated for Huy's personal portfolio tracker. Figures are model
estimates over a 3-year daily window (Jun 2023 to Jun 2026), not advice. Maths renders with MathJax
(needs an internet connection the first time you open the file).</p></div></body></html>"""

# ---------------------------------------------------------------- content ----
BODY = r"""
<span class="tag">PLAIN-ENGLISH GUIDE</span>
<h1>Your portfolio, analysed like a fund manager would</h1>
<p class="sub">What every number in the analytics notebook actually means, with the maths, worked
examples from your own holdings, and the charts that show each idea acting on your data.</p>

<p class="lead">The notebook runs in four stages. First it estimates two things for each holding: how
much it might return, and how risky it is. Then it finds the "best" mix of your holdings. Then it
works out which positions are eating your risk budget. Finally it measures the book the way a risk
desk would: worst-case losses, drawdowns, factor bets, and crash tests. This guide explains each
piece from scratch.</p>

<div class="toc"><strong>Contents</strong>
<ol>
<li><a href="#raw">The raw material: returns</a></li>
<li><a href="#s1">Stage 1: expected return (μ) and risk (Σ)</a></li>
<li><a href="#s2">Stage 2: the efficient frontier and the best mix</a></li>
<li><a href="#s3">Stage 3: who is spending your risk budget</a></li>
<li><a href="#s4">Stage 4: the professional risk metrics</a></li>
<li><a href="#caveats">The honest caveats</a></li>
<li><a href="#glossary">Glossary</a></li>
</ol></div>

<h2 id="raw">1. The raw material: returns</h2>
<p>Everything starts with the <em>return</em>, not the price. A price on its own (silver at $60)
tells you nothing about risk. What matters is how prices <em>change</em>. The daily return is the
percentage move from one day to the next:</p>
\[ r_t = \frac{P_t - P_{t-1}}{P_{t-1}} \]
<div class="box you"><div class="h">In your portfolio</div>
If your silver ETF (SLV) closes at $59.51 one day and $60.10 the next, that day's return is
\((60.10-59.51)/59.51 = 0.99\%\). The notebook does this for every holding, every day, for three
years. That grid of daily returns is the input to everything below.</div>

<h4>Turning daily into yearly (annualising)</h4>
<p>Daily numbers are tiny and hard to compare, so we scale them to a yearly figure. There are about
252 trading days in a year. Average returns scale by 252; risk (which grows with the square root of
time) scales by \(\sqrt{252}\approx 15.9\):</p>
\[ \mu_{\text{year}} = \bar r_{\text{day}}\times 252, \qquad \sigma_{\text{year}} = \sigma_{\text{day}}\times\sqrt{252} \]
<p>So a holding whose daily returns wobble by 2.7% a day has an annual volatility of about
\(2.7\%\times15.9\approx 42\%\). That is roughly where your silver position sits.</p>

<h2 id="s1">2. Stage 1: expected return (μ) and risk (Σ)</h2>
<p>To compare or combine holdings you need two ingredients for each: a best guess at its future
return (called <span class="num">μ</span>, "mu"), and a measure of its risk and how it moves with
everything else (the covariance matrix <span class="num">Σ</span>, "sigma"). This stage builds both.</p>

<h3>Expected return, μ</h3>
<p>μ is just a list, one expected yearly return per holding. The hard part is estimating it, because
the past is a noisy guide to the future. The notebook computes three versions.</p>

<h4>Option A: the historical average (simple, but noisy)</h4>
<p>Take each holding's average daily return over three years and annualise it. Easy, but it trusts
the past far too much. Your quantum-computing stock QBTS averaged roughly <span class="num">+169%
a year</span> over the window. Feeding that into an optimiser would make it scream "put everything
in QBTS." That is noise, not a forecast.</p>

<h4>Option B: CAPM-implied (what we used)</h4>
<p>The Capital Asset Pricing Model says an asset should earn the risk-free rate plus a reward for the
market risk it carries. The reward is its <em>beta</em> times the market's excess return:</p>
\[ \mu_i = r_f + \beta_i\,(\mu_{\text{market}} - r_f) \]
<p>Beta (\(\beta\)) is how much the asset moves when the market moves. You get it from a simple
regression of the asset's returns on the market's returns: it is the slope of the best-fit line.
Beta 1 means it moves with the market; beta 2 means it swings twice as hard; beta 0.5, half as hard.</p>
<div class="box you"><div class="h">Worked example: your MSTR position</div>
We used the global stock market (the ACWI index) as "the market." Over the window it returned about
14.5% a year above cash, and cash (the risk-free rate \(r_f\)) is 4%. Your MicroStrategy holding has
a beta of <span class="num">2.59</span> (it swings far harder than the market). So CAPM expects:
\[ \mu_{\text{MSTR}} = 4\% + 2.59\times 14.5\% = 41.7\% \]
Compare the two methods on QBTS: history says +169% (nonsense), CAPM says a saner +51%. CAPM does not
let one lucky stock hijack the whole analysis, which is exactly why we chose it.</div>

<h4>Option C: shrinkage</h4>
<p>A middle path: pull every holding's noisy historical average part-way toward the overall average.
This "shrinks" the extreme guesses toward something more believable. We compute it for comparison but
drive the optimiser with CAPM.</p>

<h3>Risk, the covariance matrix Σ</h3>
<p>Risk is not one number per holding. Two things matter: how much each holding bounces on its own,
and whether holdings bounce <em>together</em>. Σ captures both.</p>

<h4>Volatility: how much one holding bounces</h4>
<p>Volatility is the standard deviation of returns: the typical size of a daily move, annualised. Low
volatility means a smooth ride; high means a rough one.</p>
<div class="box you"><div class="h">In your portfolio</div>
Your Syfe fund has an annual volatility around <span class="num">18%</span> (calm, because it is
itself a diversified basket). Silver is <span class="num">42%</span>, Bitcoin <span class="num">48%</span>,
and the quantum stock QBTS a wild <span class="num">134%</span>. Higher volatility is not automatically
bad, but you want to be paid for it. Stage 3 checks whether you are.</div>

<h4>Covariance and correlation: how holdings move together</h4>
<p>Covariance measures whether two holdings rise and fall in step. It is easier to read as a
<em>correlation</em>, which rescales it to between −1 and +1:</p>
\[ \rho_{ij} = \frac{\text{Cov}(r_i,r_j)}{\sigma_i\,\sigma_j} \]
<p>A correlation of +1 means two holdings move identically, 0 means no relationship, −1 means they
move opposite. This is the engine of diversification: combining holdings that are not perfectly
correlated lowers the risk of the whole more than you would expect from the parts. Σ is the full grid
of these relationships, one row and column per holding, with each holding's own variance down the
diagonal.</p>

<h4>Sample Σ versus Ledoit-Wolf (what we used)</h4>
<p>The plain "sample" covariance just measures the historical relationships directly. With many
holdings and limited history it gets noisy and unstable, which makes optimisers misbehave. The
<em>Ledoit-Wolf</em> method shrinks that noisy estimate toward a simpler, steadier structure, trading
a little bias for a lot of stability. It picks the shrinkage strength automatically, from 0 (trust the
raw data fully) to 1 (ignore it). For your book it chose just <span class="num">0.03</span>: with
three years of daily data across 19 assets, the raw estimate was already well-behaved, so barely any
correction was needed. We also compute an EWMA version, which weights recent days more heavily to stay
responsive to the current market mood.</p>

{{IMG:correlation_heatmap.png|The correlation matrix. Red squares are holdings that move together; blue move opposite; pale squares barely relate. Read it like a grid: find a row, slide across to a column, the colour is their correlation.}}

<p>The heatmap is Σ turned into correlations and coloured. The deep-red block among the crypto names
shows they move almost as one (correlations around 0.6 to 0.8), so holding six coins is closer to
holding one big bet than six separate ones. Your Syfe fund shows paler links to most things, which is
the visual signature of a genuine diversifier.</p>

<h2 id="s2">3. Stage 2: the efficient frontier and the best mix</h2>
<p>With μ and Σ in hand, you can ask the central question of portfolio theory: for a given level of
risk, what mix of holdings gives the highest expected return? Plot the best answer for every risk
level and you get the <em>efficient frontier</em>, the gentle curve below.</p>

<h4>How the optimiser thinks</h4>
<p>A portfolio's expected return is just the weighted average of its holdings, \(\mu_p=\mathbf{w}^\top\boldsymbol\mu\).
Its risk is <em>not</em> a weighted average, because of those correlations; it is
\(\sigma_p=\sqrt{\mathbf{w}^\top\Sigma\,\mathbf{w}}\). The optimiser searches over the weights
\(\mathbf{w}\) to find the best trade-off, subject to your rules: no shorting (weights ≥ 0), fully
invested (weights sum to 100%), at most 25% in any one position, and at most 20% in crypto.</p>

<h4>The Sharpe ratio and the "best" portfolio</h4>
<p>The single most useful score for a portfolio is the Sharpe ratio: return above cash, per unit of
risk. Higher is better. It answers "how much extra return am I getting for the bumpiness I endure?"</p>
\[ \text{Sharpe} = \frac{\mu_p - r_f}{\sigma_p} \]
<p>The portfolio with the highest Sharpe is the <em>max-Sharpe</em> or <em>tangency</em> portfolio.
On the chart it is the point where a straight line drawn up from the cash rate just touches the
frontier (that line is the capital market line). We also mark two reference portfolios: the
<em>minimum-variance</em> one (lowest possible risk, far left) and a <em>risk-parity</em> one (each
holding contributes the same amount of risk).</p>

{{IMG:efficient_frontier.png|The efficient frontier. Up is more return, right is more risk. The grey curve is the best achievable. Your current portfolio (red dot) sits below it, so you are taking risk you are not being fully paid for.}}

<div class="box you"><div class="h">What it says about your book</div>
Your current portfolio (red) sits a little <em>below</em> the curve: there is a portfolio with the
same risk and more expected return, or the same return for less risk. Moving to the max-Sharpe point
(green star) lifts the Sharpe ratio from <span class="num">0.76</span> to <span class="num">0.90</span>.
The big moves it wants: cut the Syfe fund from 53% to its 25% cap, shrink crypto from 16% to 3%, trim
silver, and add cheap diversifiers like emerging markets (VWO) and the Japanese bank (MUFG). Notice
the far-right dots, your quantum and metals stocks: huge risk (100%+ volatility) for return that does
not justify it, so the optimiser leaves them tiny.</div>

<h2 id="s3">4. Stage 3: who is spending your risk budget</h2>
<p>The frontier tells you the ideal mix. This stage answers a more direct question about the mix you
hold <em>today</em>: which positions are responsible for most of your risk, and are they earning it?</p>

<h4>Marginal contribution to risk (MCR)</h4>
<p>Because of correlations, you cannot just say "this 10% position is 10% of my risk." A position that
moves with everything else adds more risk than one that zigs when others zag. The marginal
contribution to risk measures how much total portfolio volatility changes if you nudge a holding up a
little. Mathematically it is the slope of portfolio risk with respect to each weight:</p>
\[ \text{MCR}_i = \frac{(\Sigma\,\mathbf{w})_i}{\sigma_p}, \qquad \text{Risk contribution}_i = w_i\times\text{MCR}_i \]
<p>The risk contributions of all holdings add up to the total portfolio volatility, so each holding's
share is a clean "% of your risk." We compare that to its share of the portfolio's expected return. A
holding that supplies more return-share than risk-share is pulling its weight (ADD); one that hogs
risk for little return is a drag (TRIM). The same test in one number is the <em>marginal Sharpe</em>,
\((\mu_i-r_f)/\text{MCR}_i\): above the portfolio's own Sharpe means add, below means trim.</p>

{{IMG:risk_addtrim.png|Each holding's return-share minus its risk-share. Green bars (right) earn their risk; red bars (left) are risk hogs. The further left, the more it is costing you in risk for what it returns.}}

<div class="box you"><div class="h">The verdict on your book</div>
Bitcoin is the worst offender: it eats <span class="num">13.5%</span> of your total risk for under
<span class="num">10%</span> of the return (marginal Sharpe 0.56, well below your 0.76). Silver is
next (18% of risk for 15% of return). The entire crypto sleeve sits on the red, trim side. Your best
risk-adjusted holdings are the Japanese bank MUFG (marginal Sharpe 1.59), emerging markets, Oracle,
and Constellation. One subtlety: the Syfe fund shows green (it earns its risk), so the reason to trim
it is not poor returns, it is concentration, having half your money in one product.</div>

<h2 id="s4">5. Stage 4: the professional risk metrics</h2>
<p>This is the risk desk's standard toolkit, measured on your current book over the three years.</p>

<h3>Worst-case losses: VaR and Expected Shortfall</h3>
<p>Value at Risk (VaR) answers "on a normal bad day, how much could I lose?" The 99% one-day VaR is
the loss you would only exceed on the worst 1% of days. Expected Shortfall (ES, also called CVaR) goes
further: it is the <em>average</em> loss on those worst days, so it captures how bad the tail really
is. We read both straight off your actual return history rather than assuming a bell curve, so fat
tails are included.</p>
<div class="box you"><div class="h">In dollars</div>
On your roughly $50,500 analysed book: a 95% one-day VaR of 1.8% means a typical bad day is about
<span class="num">−$915</span>. The 99% VaR is 3.3% (about <span class="num">−$1,650</span>), and on
those worst days the average loss (ES) is 4.7%, roughly <span class="num">−$2,370</span>.</div>

<h3>Drawdown and Calmar</h3>
<p>A drawdown is how far you are below your previous peak. The maximum drawdown is the worst such drop
over the period, the number that actually tests your nerve. Calmar is annual return divided by that
worst drawdown: reward per unit of "worst pain."</p>
{{IMG:drawdown.png|The underwater chart. Each dip shows how far below the previous high-water mark the portfolio fell. Your deepest was about −18%.}}
<p>Your worst peak-to-trough fall was <span class="num">−18.4%</span>, and with a 35% annual return
that is a Calmar of <span class="num">1.91</span>, which is healthy.</p>

<h3>Sharpe versus Sortino</h3>
<p>Sharpe penalises all volatility, up and down. But you do not mind upside surprises. Sortino fixes
this by dividing excess return only by <em>downside</em> deviation (the wobble of losing days). Your
Sharpe is <span class="num">1.54</span> and Sortino <span class="num">2.19</span>; the gap means a fair
chunk of your "risk" is actually pleasant upside volatility.</p>
<div class="box warn"><div class="h">Two Sharpe numbers, do not mix them</div>
Stage 2 reported a Sharpe of 0.76 and Stage 4 reports 1.54. They are different on purpose. Stage 2
uses <em>forward-looking</em> CAPM returns (deliberately conservative). Stage 4 uses what actually
happened (a bull market, hence higher). One is a forecast, the other is history.</div>

<h3>Versus a benchmark: beta, tracking error, information ratio</h3>
<p>Compared with global equities (ACWI): your <em>beta</em> is 1.09 (slightly punchier than the
market). <em>Tracking error</em> is how far your returns stray from the benchmark, 13.1% a year here,
which is large because crypto, silver and single stocks pull you away from a plain index. The
<em>information ratio</em> is your return above the benchmark divided by that tracking error, a score
for active skill; yours is <span class="num">1.02</span> (you beat global equities by 13.3% a year,
though with big deviations). Over a different period that active bet could just as easily hurt.</p>

<h3>How concentrated are you really? (HHI)</h3>
<p>The Herfindahl index adds up the squares of your weights. Its reciprocal is the "effective number
of holdings." On the surface your book scores like just <span class="num">3.1</span> holdings, because
the Syfe fund, silver and Bitcoin dominate. But the Syfe fund is itself ten ETFs, so looking
<em>through</em> it, you really hold about <span class="num">12</span> distinct things. So you are less
concentrated than the headline suggests, thanks to the fund doing diversification work inside.</p>

<h3>Factor exposures: what bets are you really making?</h3>
<p>Individual tickers hide common themes. A factor regression explains your daily returns using a few
well-known style "factors" (the market, plus small-versus-large, value-versus-growth, momentum, and
quality), each proxied by a tradeable ETF. The regression returns a <em>beta</em> for each factor (how
exposed you are) and an \(R^2\) (how much of your movement those factors explain).</p>
<table><thead><tr><th>Factor</th><th>Your beta</th><th>Reading</th></tr></thead><tbody>
<tr><td>Market</td><td>+0.87</td><td>strong general equity exposure</td></tr>
<tr><td>Size (small−large)</td><td>+0.38</td><td>tilted to smaller companies</td></tr>
<tr><td>Value (value−growth)</td><td>−0.20</td><td>mild growth tilt</td></tr>
<tr><td>Momentum</td><td>+0.13</td><td>slight momentum</td></tr>
<tr><td>Quality</td><td>−0.38</td><td>tilted to lower-quality, speculative names</td></tr>
</tbody></table>
<p>The picture is a "speculative small-cap" tilt, the small, lower-quality names you hold. The
\(R^2\) is <span class="num">0.63</span>, so equity factors explain about two-thirds of your swings;
the other third is crypto and silver doing their own thing, which no stock factor captures.</p>

<h3>Where your money actually sits (region, look-through)</h3>
<p>Decomposing the Syfe fund into its underlying ETFs, your true geographic exposure is roughly 46%
United States, 16% silver, 16% crypto, 11% developed markets outside the US, 5% emerging markets, and
3% China. Useful for spotting hidden concentration, in your case a heavy US and commodity tilt.</p>

<h3>Stress tests: what if?</h3>
<p>Rather than wait for a crash, we apply hypothetical shocks and read off the damage. Equity shocks
flow through each holding by its beta (so high-beta names fall more); crypto shocks hit the coins
directly.</p>
{{IMG:stress_tests.png|Estimated portfolio loss under four scenarios. A broad equity crash hurts most because most of your money is equity-like.}}
<p>A global equity fall of 20% would cost you about <span class="num">−17.5%</span> (roughly −$8,800);
a 50% crypto crash about −8% (−$4,000); a broad risk-off day around −18%. Equities are your dominant
risk, not crypto, simply because there is far more equity in the book.</p>

<h3>The backtest, and the most important lesson here</h3>
{{IMG:backtest.png|Growth of $1 over three years for your current weights versus the two optimised portfolios, rebalanced daily. Your current mix (red) finished highest.}}
<div class="box warn"><div class="h">Read this twice</div>
Your current portfolio returned <span class="num">+155%</span> over three years. The "optimised"
max-Sharpe portfolio returned only +123%, and the low-risk one +111%. So the optimiser would have made
you <em>less</em> money. That is not a bug. The optimiser trims exactly the crypto and silver that
happened to soar, in exchange for a smoother ride and a better <em>expected</em> risk-adjusted return
going forward. Over a boom, more risk wins. The optimiser is a risk-management tool, not a
crystal ball or a promise of higher returns. Whether the next three years reward risk the way the last
three did is the actual bet you are making.</div>

<h2 id="caveats">6. The honest caveats</h2>
<p>A few things to keep in mind so you read the numbers with the right amount of trust.</p>
<p>Optimisers are very sensitive to the return guesses you feed them. Small changes in μ swing the
recommended weights hard, which is why the trustworthy signal is the <em>direction</em> (you are
over-concentrated in one fund and over-exposed to crypto for its risk), not the exact percentages.</p>
<p>Three years is a short, and unusually strong, window. Volatilities, correlations and especially
returns will look different in a downturn. Crypto's low measured "risk" here partly reflects a calm,
rising market.</p>
<p>SpaceX was excluded from the maths because it has only days of history; you cannot estimate risk
from a handful of points. It still sits in your portfolio, just not in this analysis. And the whole
thing assumes today's holdings were held throughout, since there is no trade history, so it is a
"what your current basket would have done," not your exact past account.</p>

<h2 id="glossary">7. Glossary</h2>
<table><thead><tr><th>Term</th><th>Plain meaning</th></tr></thead><tbody>
<tr><td>Return</td><td>Percentage change in price from one day to the next.</td></tr>
<tr><td>μ (mu)</td><td>Expected future return, one per holding.</td></tr>
<tr><td>Σ (sigma)</td><td>The grid of risks and how holdings move together (covariance).</td></tr>
<tr><td>Volatility</td><td>Standard deviation of returns; the size of typical bounces.</td></tr>
<tr><td>Correlation</td><td>How two holdings move together, from −1 to +1.</td></tr>
<tr><td>Beta</td><td>How hard a holding swings when the market swings.</td></tr>
<tr><td>CAPM</td><td>A model: expected return = cash + beta × market reward.</td></tr>
<tr><td>Ledoit-Wolf</td><td>A steadier way to estimate Σ by shrinking noisy estimates.</td></tr>
<tr><td>Efficient frontier</td><td>The best return achievable at each level of risk.</td></tr>
<tr><td>Sharpe ratio</td><td>Return above cash per unit of total risk. Higher is better.</td></tr>
<tr><td>Sortino ratio</td><td>Like Sharpe, but only penalises downside risk.</td></tr>
<tr><td>Tangency / max-Sharpe</td><td>The single best-Sharpe portfolio on the frontier.</td></tr>
<tr><td>MCR</td><td>How much portfolio risk changes if you add a sliver of a holding.</td></tr>
<tr><td>VaR</td><td>A loss you would only exceed on the worst few percent of days.</td></tr>
<tr><td>Expected Shortfall</td><td>The average loss on those worst days (the tail).</td></tr>
<tr><td>Max drawdown</td><td>The worst peak-to-trough fall over the period.</td></tr>
<tr><td>Calmar</td><td>Annual return divided by the worst drawdown.</td></tr>
<tr><td>Tracking error</td><td>How far your returns stray from a benchmark.</td></tr>
<tr><td>Information ratio</td><td>Return above a benchmark per unit of tracking error.</td></tr>
<tr><td>HHI</td><td>A concentration score; its reciprocal is the effective number of holdings.</td></tr>
<tr><td>Factor exposure</td><td>How much of your return is explained by common style bets.</td></tr>
</tbody></table>
"""

for marker in []:
    pass


def build():
    body = BODY
    # replace {{IMG:file|caption}} markers with embedded figures
    while "{{IMG:" in body:
        a = body.index("{{IMG:")
        b = body.index("}}", a)
        inner = body[a + 6:b]
        fname, caption = inner.split("|", 1)
        body = body[:a] + fig(fname.strip(), caption.strip()) + body[b + 2:]
    html = HEAD + body + FOOT
    DEST.write_text(html, encoding="utf-8")
    print(f"wrote {DEST}  ({len(html)/1024:.0f} KB)")


if __name__ == "__main__":
    build()
