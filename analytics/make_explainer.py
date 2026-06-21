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
<li><a href="#exante">How to read these numbers: ex-ante vs ex-post</a></li>
<li><a href="#raw">The raw material: returns</a></li>
<li><a href="#s1">Stage 1: expected return (μ) and risk (Σ)</a></li>
<li><a href="#s2">Stage 2: the efficient frontier and the best mix</a></li>
<li><a href="#s3">Stage 3: who is spending your risk budget</a></li>
<li><a href="#s4">Stage 4: the professional risk metrics</a></li>
<li><a href="#mc">Stage 5: Monte Carlo, your year ahead in 10,000 futures</a></li>
<li><a href="#verdict">What it all means, and what to consider doing</a></li>
<li><a href="#gaps">Where you are under-exposed, and a watchlist</a></li>
<li><a href="#road">The road ahead: what to do with this portfolio</a></li>
<li><a href="#missing">Metrics and methods you are not yet using</a></li>
<li><a href="#adv">The advanced methods, applied to your book</a></li>
<li><a href="#caveats">The honest caveats</a></li>
<li><a href="#glossary">Glossary</a></li>
</ol></div>

<h2 id="exante">How to read these numbers: ex-ante vs ex-post</h2>
<p>One distinction shapes how you read everything below. Some numbers look <em>forward</em> (ex-ante):
forecasts and decisions about what to expect or do next. Others look <em>backward</em> (ex-post): a
record of what actually happened. Mixing them up is the most common way to misread a portfolio report.</p>
<p>A few inputs sit in between: they are <em>measured</em> from the past but <em>used</em> for the
future. Risk and correlation are far steadier over time than returns, so estimating them from history
and projecting them forward is reasonable. Returns are not steady, which is exactly why we forecast
them with CAPM rather than trusting the past.</p>
<table><thead><tr><th>Number</th><th>Looking</th><th>What it is for</th></tr></thead><tbody>
<tr><td>CAPM expected returns (μ)</td><td>Ex-ante</td><td>The forward return forecast that drives every decision.</td></tr>
<tr><td>Optimisation: frontier, max-Sharpe weights, expected Sharpe</td><td>Ex-ante</td><td>What mix to hold next, and the risk and return you expect from it.</td></tr>
<tr><td>Risk decomposition (MCR, marginal Sharpe, add/trim)</td><td>Ex-ante</td><td>Which positions to scale up or down from here.</td></tr>
<tr><td>Monte Carlo (parametric)</td><td>Ex-ante</td><td>The range of possible future outcomes, and the chance of a loss.</td></tr>
<tr><td>Covariance Σ, volatility, correlation, beta</td><td>Measured ex-post, used ex-ante</td><td>The forward risk inputs: read from history, projected forward.</td></tr>
<tr><td>Value at Risk, Expected Shortfall</td><td>Measured ex-post, used ex-ante</td><td>A forward loss budget, read off the past loss distribution.</td></tr>
<tr><td>Realised return (CAGR), realised Sharpe, Sortino, Calmar</td><td>Ex-post</td><td>Your actual track record, and how the ride felt.</td></tr>
<tr><td>Maximum drawdown</td><td>Ex-post</td><td>The worst peak-to-trough fall that actually happened.</td></tr>
<tr><td>Beta, tracking error, information ratio vs ACWI</td><td>Ex-post</td><td>How you actually did against the benchmark.</td></tr>
<tr><td>Treynor, Jensen's alpha, up/down capture, hit rate</td><td>Ex-post</td><td>Risk-adjusted skill, capture and consistency, all read off the realised record.</td></tr>
<tr><td>Factor exposures and R²</td><td>Ex-post</td><td>Which style bets actually drove your past returns.</td></tr>
<tr><td>Skew, kurtosis, Omega, tail ratio, M², appraisal, drawdown duration</td><td>Ex-post</td><td>A deeper read of the shape of your realised returns and the quality of your alpha.</td></tr>
<tr><td>Stage 6: Black-Litterman, CVaR optimisation, regime Monte Carlo, scenario stress</td><td>Ex-ante</td><td>Forward-looking portfolio decisions and tail-risk estimates.</td></tr>
<tr><td>Stage 6: return attribution, factor-risk decomposition</td><td>Ex-post</td><td>What actually drove your realised return and your realised risk.</td></tr>
<tr><td>Backtest (current +155% vs optimised +123%)</td><td>Ex-post</td><td>How the mixes would have performed over the window.</td></tr>
<tr><td>Historical-average μ, bootstrap simulation</td><td>Ex-post</td><td>Pure history, shown only for comparison.</td></tr>
</tbody></table>
<p>The cleanest example of the gap is the two Sharpe ratios. The ex-ante one (0.76) is a forecast for
the mix you hold; the ex-post one (1.54) is what the ride actually delivered in a strong market. The
backtest is pure ex-post: your current book beat the optimised one historically, even though the
ex-ante optimiser expects the optimised one to do better from here. Neither is wrong; they answer
different questions.</p>

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

<h3>Expected return, μ: which method, and why</h3>
<p>μ is just a list, one expected yearly return per holding. Estimating it is the hard part, because
the past is a noisy guide to the future. The notebook computes three different estimates, but it does
not use them equally.</p>
<div class="box"><div class="h">Which method actually drives the analysis</div>
Every forward-looking number in this report, the optimisation, the efficient frontier, and the Monte
Carlo simulation, is driven by the <em>CAPM-implied</em> returns (method 2 below). The historical and
shrinkage estimates are computed only so you can see how noisy the raw history is. Nothing downstream
uses them.</div>

<h4>Method 1: the historical average (computed, not used)</h4>
<p>Take each holding's average daily return over three years and annualise it. Simple, but it trusts
the past far too much. Your quantum stock QBTS averaged about <span class="num">+169% a year</span>
over the window; your bioplastics stock ORGN about <span class="num">−85%</span>. Feed those into an
optimiser and it piles into QBTS and refuses to touch ORGN, on the strength of three years of luck.
That is noise, not a forecast, which is why we leave it out.</p>

<h4>Method 2: CAPM-implied (this is the one we use)</h4>
<p>The Capital Asset Pricing Model ties an asset's expected return to the one risk the market actually
pays you for: how much it moves with the market as a whole. The formula is short.</p>
\[ \mu_i = r_f + \beta_i\,(\mu_{\text{market}} - r_f) \]
<p>Read it as cash, plus your sensitivity to the market (\(\beta_i\)) times the market's reward for
taking risk. Here is the exact four-step process the notebook runs:</p>
<ol>
<li>Pick the market. We use the global stock index ACWI as the stand-in for "the market."</li>
<li>Measure each holding's beta. Beta comes from a linear regression of the holding's daily returns
against the market's daily returns over the three years. The slope of that best-fit line is the beta.
Beta 1 means it moves with the market; beta 2 swings twice as hard; beta 0.5, half as hard.</li>
<li>Measure the market's reward (the equity risk premium): the market's own average return above cash
over the window. Here that came to <span class="num">14.5%</span> a year.</li>
<li>Combine. Plug beta and the premium into the formula, with cash at 4%.</li>
</ol>
<div class="box you"><div class="h">Worked example, end to end: your MSTR</div>
Step 2 gives MicroStrategy a beta of <span class="num">2.59</span> (it swings far harder than the
market). Step 3 gives a premium of 14.5%. Step 4:
\[ \mu_{\text{MSTR}} = 4\% + 2.59\times 14.5\% = 41.7\% \]
The discipline shows on the wild names: history said QBTS would earn +169% a year, CAPM says a saner
<span class="num">+51%</span>; history said ORGN would lose 85%, CAPM says <span class="num">+27%</span>.
CAPM will not let one lucky or unlucky stretch hijack the forecast, because it forces every return to
be justified by the holding's market risk, not its recent luck. That stability is what an optimiser
needs.</div>

<h4>Method 3: shrinkage (computed, not used)</h4>
<p>A halfway house: take the noisy historical averages and pull each one part-way toward the overall
average, so the extremes calm down. Steadier than raw history, but still anchored to the past. We
report it beside the others for comparison and leave it there.</p>

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

<h3>Return per unit of <em>market</em> risk: Treynor and Jensen's alpha</h3>
<p>Sharpe divides your excess return by <em>total</em> risk. But in a diversified book the risk that
"deserves" a reward is only the part you cannot diversify away, the market (beta) risk. Two classic
measures judge you on that instead.</p>
<p>The <strong>Treynor ratio</strong> is excess return per unit of beta:</p>
\[ \text{Treynor} = \frac{R_p - R_f}{\beta_p} = \frac{35.1\% - 4\%}{1.09} \approx 0.29 \]
<p>The benchmark itself has a beta of 1.0, so its Treynor is just its own excess return, about
<span class="num">0.155</span>. You score <span class="num">0.29</span>, nearly <em>double</em>, meaning
you have earned almost twice the reward per unit of market risk that global equities did. Treynor is
the right lens when beta is the risk you care about; Sharpe is the right lens when total volatility is.</p>
<p><strong>Jensen's alpha</strong> asks the sharper question: given how much market risk you took, what
return <em>should</em> you have earned, and did you beat it? CAPM predicts a fair return of
\( R_f + \beta_p(R_m - R_f) \), and your alpha is whatever you made above that line:</p>
\[ \begin{aligned} \alpha_J &= R_p - \big[\,R_f + \beta_p (R_m - R_f)\,\big] \\ &= 35.1\% - \big(\,4\% + 1.09 \times 15.5\%\,\big) = +14.2\% \end{aligned} \]
<p>Your beta alone "entitled" you to about a 21% return; you made 35%, so roughly
<span class="num">+14% a year</span> is outperformance that market risk does not explain. Reassuringly,
it lines up with your factor-regression alpha (+12.6%) and your active return (+13.3%), three different
methods agreeing the edge was real, at least over this window.</p>

<h3>Up and down capture, and hit rate</h3>
<p><strong>Capture ratios</strong> split the benchmark's months into the ones it rose and the ones it
fell, then ask how much of each move you caught. Up-capture is your compounded return in ACWI's up
months divided by ACWI's; down-capture is the same for its down months.</p>
<table><thead><tr><th>Measure</th><th>You</th><th>Reading</th></tr></thead><tbody>
<tr><td>Up-capture</td><td>179%</td><td>In rising months you gained about 1.8&times; what the market did, you amplify rallies.</td></tr>
<tr><td>Down-capture</td><td>97%</td><td>In falling months you lost slightly <em>less</em> than the market, marginally defensive.</td></tr>
</tbody></table>
<p>The prize is the combination. Catching far more of the upside (179%) than the downside (97%) is
exactly the asymmetry a fund manager hunts for, and it is where most of your alpha comes from. The
honest caveat: this is measured over a boom, so the gaudy up-capture partly reflects crypto and silver
soaring, do not bank on 179% in the next real downturn.</p>
<div class="box warn"><div class="h">Capture vs the stress test, not a contradiction</div>
Down-capture (97%) says you historically fell a touch <em>less</em> than ACWI, yet the stress test
below says a 20% market crash costs you about 17.5%. Both are right: capture is what
<em>actually</em> happened, where your stock-picking gains offset many market dips; the stress test
switches that luck off and shocks the market alone. Capture is your record; the stress test is a
deliberately pessimistic what-if.</div>
<p>The <strong>hit rate</strong> is a breadth check, are your gains broad or one fluke? Of your 19
positions, <span class="num">14 (74%)</span> are in profit over the window, and
<span class="num">65%</span> of your months were positive. Both being comfortably above half says the
performance is well spread and reasonably consistent, not a single lucky position carrying everything.
A strong return paired with a <em>low</em> hit rate would be the warning sign; yours is the opposite.</p>

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

<h2 id="mc">6. Stage 5: Monte Carlo, your year ahead in 10,000 futures</h2>
<p>Every number so far is a single best estimate. Monte Carlo asks a different question: given those
estimates, what is the whole <em>range</em> of where you could end up in a year? It rolls the dice
10,000 times.</p>
<h4>The method</h4>
<p>For each of 10,000 simulated years, it draws a random return for every trading day and compounds
them into a final value. The dice are loaded by your inputs: the average drift comes from the CAPM
expected return, and the size and correlation of the random shocks come from the Ledoit-Wolf Σ. This
is geometric Brownian motion, the standard model for asset paths. A second version resamples actual
historical days (a "bootstrap"), which keeps real-world fat tails but replays the recent boom.</p>
{{IMG:montecarlo_fan.png|10,000 simulated one-year paths. The dark line is the median outcome; the bands show the middle 50% and the middle 90% of futures. The cone widens because uncertainty compounds over time.}}
<p>Reading the fan: starting near $50,500, the typical (median) year ends around
<span class="num">$60,500</span> (+20%). The spread is wide. The worst 5% of years end below about
<span class="num">$42,700</span> (−15%, roughly −$7,900), and the best 5% above
<span class="num">$85,900</span> (+70%).</p>
{{IMG:montecarlo_dist.png|The 10,000 final outcomes as a histogram, your current mix (red) against the optimised max-Sharpe mix (green). Bars to the left of zero are losing years.}}
<div class="box you"><div class="h">What the dice say</div>
On forward assumptions your current book has about a <span class="num">20%</span> chance of ending the
year down, with a bad-case loss near −$7,900. The optimised mix (green) has a thinner left tail: the
chance of a down year falls to about <span class="num">16%</span> and the bad case to −11%, for a
similar typical return. That is the whole case for optimising, fewer ugly years for the same expected
reward. The rosier bootstrap result (only a 7% chance of loss) just assumes the next year looks like
the last three, so treat it as the optimistic bookend, not the base case.</div>

<h2 id="verdict">7. What it all means, and what to consider doing</h2>
<p>Here is the plain-English "so what" for each measure — now with a concrete <em>action</em> beside it —
then which positions to trim, how to rebalance, and the warning signs to watch. None of this is advice;
it is what the analysis suggests, and the decisions are yours.</p>
<h3>What each number implies for you, and what to do</h3>
<table><thead><tr><th>Measure</th><th>Your number</th><th>What it means for you</th><th>Action</th></tr></thead><tbody>
<tr><td>Sharpe ratio</td><td>0.76 (0.90 reachable)</td><td>A fair reward for your risk, but you are leaving some on the table; the same risk could earn more.</td><td>Move part-way to the optimised mix to lift Sharpe without cutting return.</td></tr>
<tr><td>Sortino ratio</td><td>2.19</td><td>Much of your "risk" is upside surprise, not real pain. Your downside is well paid.</td><td>No change — this is a feature, not a problem.</td></tr>
<tr><td>Max drawdown / Calmar</td><td>−18% / 1.91</td><td>Be ready to see the book ~18% below a peak, maybe more ahead. The reward for that pain is healthy.</td><td>Keep enough cash that an 18–25% dip never forces a sale.</td></tr>
<tr><td>VaR / ES 99%, one day</td><td>−$1,650 / −$2,370</td><td>On a 1-in-100 day you lose ~$1,650; when it lands, the average is ~$2,370. The tail bites harder than VaR alone.</td><td>Size positions so a tail day is annoying, not destabilising.</td></tr>
<tr><td>Beta vs world stocks</td><td>1.09</td><td>You fall slightly more than global equities in a sell-off, not less.</td><td>Add defensives if you want beta nearer 1.0.</td></tr>
<tr><td>Tracking error / Information ratio</td><td>13.1% / 1.02</td><td>You stray far from the index, and those active bets paid off — over this window.</td><td>Take big deviations only where you have real conviction.</td></tr>
<tr><td>Treynor / Jensen's alpha</td><td>0.29 / +14.2%</td><td>Per unit of market risk you roughly doubled the index, with genuine alpha on top.</td><td>Protect what's working; don't dilute the winners when you trim.</td></tr>
<tr><td>Up / down capture</td><td>179% / 97%</td><td>You amplify rallies and barely cushion falls — brilliant in a boom, punishing if the trend turns.</td><td>Lower down-capture with the quality/defensive names below.</td></tr>
<tr><td>Hit rate</td><td>74% positions / 65% months</td><td>Gains are broad and fairly steady, not one fluke carrying the book.</td><td>Keep breadth as you rebalance; don't over-concentrate.</td></tr>
<tr><td>Concentration (HHI)</td><td>3.1 (12.1 look-through)</td><td>The real concentration is half your money in one product. The fund diversifies inside.</td><td>Cap the Syfe fund's share; don't let new money pile into it.</td></tr>
<tr><td>Factor tilt</td><td>small-cap, low quality</td><td>A speculative bet that tends to lag in a flight to safety.</td><td>Add quality and large-cap to balance the tilt (watchlist below).</td></tr>
<tr><td>Equity −20% stress</td><td>−$8,800</td><td>A normal-sized bad market costs you roughly this.</td><td>Pre-decide your response so a −$8k month isn't a shock.</td></tr>
<tr><td>Monte Carlo chance of loss</td><td>~20% (bad case −$7,900)</td><td>About a 1-in-5 chance of a down year.</td><td>If that's uncomfortable, shift toward the optimised mix.</td></tr>
</tbody></table>

<h3>Which positions to trim or cut, and why</h3>
<p>Three independent methods — the optimiser, the risk decomposition (Stage 3), and the simulation —
point at the same names. The test is simple: is a position eating more of your risk budget than it
pays back?</p>
<table><thead><tr><th>Position</th><th>Now</th><th>The issue</th><th>Suggested</th></tr></thead><tbody>
<tr><td><strong>Bitcoin</strong></td><td>largest coin</td><td>Your single biggest risk hog: high volatility, and it moves with the other coins, so it adds little diversification for the risk it costs.</td><td>Trim hard</td></tr>
<tr><td><strong>Silver (SLV)</strong></td><td>~16% (commodity)</td><td>Stage 3's other risk hog — uses more of your risk budget than it returns on a forward basis.</td><td>Trim</td></tr>
<tr><td><strong>Crypto sleeve (6 coins)</strong></td><td>~16%</td><td>So correlated (the red block in the heatmap) that the six behave like one bet, not six. The optimiser wants nearer 3%.</td><td>Cut toward ~5–8%</td></tr>
<tr><td><strong>Syfe Core Equity100</strong></td><td>~53%</td><td>Not a quality problem — it's efficient and diversified inside — but it's a single-product dependence.</td><td>Cap, don't grow</td></tr>
</tbody></table>
<p>The honest caveat (see the box below): these are the names that <em>soared</em>, so trimming them
would have lowered your past return. The case for trimming is forward-looking risk control, not a
prediction that they will fall.</p>

<h3>How to rebalance, in practice</h3>
<ul>
<li><strong>Use bands, not a calendar.</strong> Set a target weight per sleeve (say crypto 8%, Syfe 45%) and only act when a holding drifts more than ~5 percentage points off target. Less needless trading.</li>
<li><strong>Rebalance with new money first.</strong> Direct fresh contributions into the under-weight sleeves (healthcare, quality, ex-US) rather than selling winners — it avoids tax and fees entirely.</li>
<li><strong>Trim gradually.</strong> Scale out of Bitcoin and silver in steps, not one trade. You keep some upside if the boom runs, while steadily de-risking.</li>
<li><strong>Mind the FX.</strong> You hold USD assets and live in SGD; rebalancing across the two adds an FX leg each time. Batch trades to limit conversion spread.</li>
<li><strong>Net off costs and tax.</strong> Singapore has no capital-gains tax, which helps — but spreads, platform fees and US dividend withholding still apply. Subtract them from any expected gain before you trade.</li>
</ul>

<h3>Warning signs — when rebalancing can hurt</h3>
<ul>
<li><strong>Selling winners into a trend.</strong> Momentum is real; trimming a runner too early has a cost. Bands and gradual exits guard against it.</li>
<li><strong>Chasing the optimiser's exact numbers.</strong> Small changes in the return guesses swing the "optimal" weights wildly. Trust the <em>direction</em> (less crypto, more quality), not the decimals.</li>
<li><strong>Over-trading.</strong> Every rebalance costs spread and fees. If the benefit is smaller than the cost, don't.</li>
<li><strong>Acting on noise.</strong> A 2% wobble is not a signal. Wait for the band breach.</li>
<li><strong>Forgetting why you own it.</strong> If the thesis is intact, a dip is not a reason to sell — and a spike is not, by itself, a reason to buy more.</li>
</ul>
<div class="box warn"><div class="h">The honest tension, and a disclaimer</div>
Over the last three years your riskier current book (+155%) beat the optimised one (+123%), because the
optimiser trims exactly the crypto and silver that soared. The optimiser lowers risk; it does not
promise higher returns. So the real decision is your own view on whether the next few years reward risk
the way the last few did. And to be clear: this is analysis, not financial advice. I am not a licensed
adviser, and every decision here is yours to make.</div>

<h2 id="gaps">8. Where you are under-exposed, and a watchlist</h2>
<p>Your look-through exposure says what you <em>don't</em> own as loudly as what you do. The map: 46%
United States, ~16% silver, ~16% crypto, 11% developed markets ex-US, 5% emerging, 3% China — and
almost nothing in Japan. By sector and style you tilt to small, speculative, lower-quality growth, with
<strong>no meaningful healthcare, no energy, and no defensive ballast.</strong> Those are exactly the
things that hold up when the speculative trade breaks.</p>
<table><thead><tr><th>Gap</th><th>Why it matters</th><th>Fills it</th></tr></thead><tbody>
<tr><td>Healthcare</td><td>Defensive demand, an ageing world, currently out of favour — the classic ballast you lack.</td><td>UNH, XLV</td></tr>
<tr><td>Energy</td><td>An inflation and geopolitics hedge that pays you to wait via dividends. Zero exposure today.</td><td>XLE, CVX</td></tr>
<tr><td>Quality / defensives</td><td>Directly offsets your "low quality" factor tilt and your 179%-up / 97%-down profile.</td><td>BRK-B, quality ETFs (QUAL)</td></tr>
<tr><td>Developed ex-US / Japan</td><td>Cheap diversification; Japan is ~0% of your book today.</td><td>EFA (held inside Syfe), MUFG</td></tr>
</tbody></table>

<h3>The watchlist, with live numbers</h3>
<p>A quick, current read (prices to 18 Jun 2026, pulled live; valuations approximate). These are
candidates to <em>research</em>, not recommendations.</p>
<table><thead><tr><th>Ticker</th><th>What</th><th>Price</th><th>YTD / 1Y</th><th>Yield</th><th>The one-line thesis</th></tr></thead><tbody>
<tr><td><strong>UNH</strong></td><td>UnitedHealth — health insurer</td><td>$401</td><td>+21% / +37%</td><td>~2.3%</td><td>Quality compounder that de-rated on one-off legal and Medicare scares; forward P/E ~19 vs trailing ~30 says the market expects an earnings rebound. Still below its old highs.</td></tr>
<tr><td><strong>XLV</strong></td><td>US health-care sector ETF</td><td>$149</td><td>−4% / +15%</td><td>~1.7%</td><td>The whole sector in one ticker — diversifies the single-stock risk of UNH while filling the same gap.</td></tr>
<tr><td><strong>XLE</strong></td><td>US energy sector ETF</td><td>$54</td><td>+19% / +28%</td><td>~2.6%</td><td>Broad energy in one line; an inflation and geopolitics hedge your book completely lacks.</td></tr>
<tr><td><strong>CVX</strong></td><td>Chevron — integrated oil major</td><td>$174</td><td>+14% / +23%</td><td>~4.1%</td><td>Cheap (forward P/E ~14), pays ~4% to hold, defensive within energy. Income and ballast in one.</td></tr>
<tr><td><strong>BRK-B</strong></td><td>Berkshire Hathaway — quality holding co.</td><td>$489</td><td>−2% / +0%</td><td>—</td><td>Low-beta quality ballast — flat over the past year precisely because it doesn't chase the boom. That is the point: it cushions a downturn.</td></tr>
</tbody></table>

<h4>A quick read on the two industries you named</h4>
<p><strong>Healthcare</strong> has lagged (the sector ETF is −4% this year while the S&P 500 is +10%),
which is what makes it interesting: defensive, cash-generative businesses on sale because sentiment
soured on drug pricing and Medicare politics. UNH is the bellwether — its +37% over the past year is a
recovery from a brutal de-rating, and the gap between its trailing (~30) and forward (~19) P/E is the
market betting earnings normalise. The risk is that the legal and regulatory overhang lingers. As a
gap-filler it is close to ideal: it zigs when your speculative growth names zag.</p>
<p><strong>Energy</strong> has done the opposite — the sector is +28% over a year on firm oil and its
role as an inflation hedge. The appeal for <em>you</em> is diversification and income: energy has a low
correlation with your tech-and-crypto cluster, and names like Chevron pay ~4% dividends. The risks are
cyclicality (energy falls hard in a recession) and the long-run energy-transition question. A sector
ETF (XLE) spreads the single-name risk; CVX adds a cheap, high-yield anchor.</p>

<h2 id="road">9. The road ahead: what to do with this portfolio</h2>
<p>Beyond the immediate rebalance, a sensible progression — roughly in order:</p>
<ol>
<li><strong>Set a target allocation and rebalancing bands.</strong> Decide the sleeves (e.g. global equity via Syfe ~45%, single-stock satellites, crypto ≤8%, a new defensive/quality sleeve ~10–15%) and let the bands trigger trades. This turns ad-hoc decisions into a rule you can follow under stress.</li>
<li><strong>Build the defensive sleeve.</strong> Phase in healthcare, energy and quality from the watchlist using new contributions. The goal: pull your down-capture below 100% and beta toward 1.0 without giving up much upside.</li>
<li><strong>Add an income / ballast layer as the book grows.</strong> Short-dated Treasuries or a money-market holding (yielding ~4–5% now) give you dry powder for the next drawdown and lower whole-portfolio volatility.</li>
<li><strong>Start the options journey deliberately.</strong> You are building toward derivatives — the two lowest-risk first steps fit your book perfectly:
  <ul>
  <li><strong>Covered calls</strong> on a position you would happily trim: sell upside you don't mind giving up, collect the premium.</li>
  <li><strong>Protective puts</strong> on your most volatile names: cheap, defined insurance against the fat left tail the kurtosis flagged.</li>
  </ul>
  Both are <em>risk-reducing</em> uses of options. Learn these before anything that adds leverage.</li>
<li><strong>Instrument the portfolio.</strong> Track the metrics in this report over time, not just once. A rising tracking error or a falling hit rate is an early warning that your edge is fading.</li>
<li><strong>Revisit the estimates quarterly.</strong> Re-run μ/Σ and the optimiser each quarter, and after any large contribution or market move. The three-year window slowly takes in the next regime, and the numbers will shift with it.</li>
</ol>

<h2 id="missing">10. Metrics and methods you are not yet using</h2>
<p>Your toolkit is strong on the basics but blind in three places: the <em>shape</em> of your returns
(not just their average and spread), the <em>quality</em> of your alpha, and how <em>long</em> you stay
in pain. I have added the cheap, high-value ones to the notebook — here they are on your data.</p>
{{IMG:returns_hist.png|Your actual daily returns (blue) against a normal bell curve with the same average and spread (red). The taller peak and the fatter edges are the "fat tails": extreme days, good and bad, happen more often than a bell curve assumes.}}
<table><thead><tr><th>Metric</th><th>You</th><th>What it adds</th></tr></thead><tbody>
<tr><td>Skewness</td><td>−0.29</td><td>Your returns lean slightly toward crash-style down-days — a mild negative skew the Sharpe ratio cannot see.</td></tr>
<tr><td>Excess kurtosis</td><td>+3.05</td><td>Fat tails: extreme days (both directions) are far more common than a bell curve predicts. Your risk lives in the tails.</td></tr>
<tr><td>Omega ratio</td><td>1.31</td><td>Weighing every gain against every loss, you make $1.31 for each $1 you lose — a fuller picture than Sharpe.</td></tr>
<tr><td>Tail ratio</td><td>1.15</td><td>Your biggest up-days slightly beat your biggest down-days: a mild edge even in the extremes.</td></tr>
<tr><td>M² (at market risk)</td><td>25.8%</td><td>Dialled down to the market's volatility, your skill still translates to a 25.8% return — about +6.3% over the index, risk-matched.</td></tr>
<tr><td>Appraisal ratio</td><td>1.03</td><td>Your alpha per unit of stock-specific risk. Near 1.0 is institutional-grade — the edge is real, not just extra beta.</td></tr>
<tr><td>Cornish-Fisher VaR</td><td>−2.0%</td><td>The normal-curve VaR (−1.8%) understates the danger; adjusting for your skew and fat tails widens the daily loss to −2.0%.</td></tr>
<tr><td>Longest drawdown</td><td>~5 months</td><td>The longest you sat below a previous peak (102 trading days). The −18% depth is only half the story; this is the <em>duration</em> of the pain.</td></tr>
</tbody></table>
<p>Two small formulae worth knowing. The Omega ratio weighs gains against losses around a threshold
\( \tau \):</p>
\[ \Omega(\tau) = \frac{\int_\tau^{\infty}\big(1-F(r)\big)\,dr}{\int_{-\infty}^{\tau}F(r)\,dr} \]
<p>and M² rescales your Sharpe to the benchmark's risk, so you can compare in plain return terms:</p>
\[ M^2 = R_f + \text{Sharpe}_p \times \sigma_{\text{benchmark}} = 4\% + 1.54 \times 14.2\% \approx 25.8\% \]

<h3>Bigger methods — now built into the notebook</h3>
<p>These were a wishlist; they are now all implemented in Stage 6. Each fixes a real limitation of what
you had. <a href="#adv">Section 11</a> walks through what every one of them found on your actual book.</p>
<table><thead><tr><th>Method</th><th>What it fixes</th></tr></thead><tbody>
<tr><td><strong>Black-Litterman</strong></td><td>Blends <em>your</em> views with the market's implied returns, so the optimiser stops producing extreme weights from noisy μ guesses. The single biggest upgrade to your Stage 2.</td></tr>
<tr><td><strong>CVaR / tail optimisation</strong></td><td>Optimises against expected shortfall (the fat left tail) instead of variance — a better fit for a book with +3 kurtosis like yours.</td></tr>
<tr><td><strong>Performance attribution (Brinson)</strong></td><td>Splits your return into how much came from <em>where</em> you allocated vs <em>which</em> names you picked. Tells you whether the edge is selection or luck.</td></tr>
<tr><td><strong>Regime / fat-tailed Monte Carlo</strong></td><td>Your current simulation assumes calm, normal days. Student-t or regime-switching paths build in crashes — more honest tail estimates.</td></tr>
<tr><td><strong>Factor risk model</strong></td><td>Decompose <em>risk</em> (not just return) into factor exposures, so you see which bets drive your volatility, not only your performance.</td></tr>
<tr><td><strong>Transaction-cost & turnover modelling</strong></td><td>Charges for every trade, turning "the optimiser wins on paper" into a net-of-costs answer.</td></tr>
<tr><td><strong>Liquidity & bespoke scenario stress</strong></td><td>Beyond market shocks: how fast could you exit, and tailored scenarios (a rate spike, a crypto winter) built on your actual holdings.</td></tr>
</tbody></table>
<p>Of these, <strong>Black-Litterman</strong> and <strong>CVaR optimisation</strong> give you the most
for the least effort, and are the two worth keeping in regular use.</p>

<h2 id="adv">11. The advanced methods, applied to your book</h2>
<p>The seven methods from the wishlist above are now built into the notebook (Stage 6). Here is what
each one says about your actual portfolio — the tools that turn good retail analysis into something
closer to a desk process.</p>

<h3>1 — Black-Litterman: steadier optimiser inputs</h3>
<p>The plain optimiser is famously twitchy: feed it noisy return guesses and it lurches to extreme
weights. Black-Litterman fixes that by starting from the returns your current book <em>implies</em>,
then nudging them with a few explicit <em>views</em> of yours. I encoded three views that mirror your
trim signals — the crypto sleeve returns only 8%, silver only 6%, and quality (MUFG) beats crypto by
5%. The result is a <em>more</em> diversified optimal portfolio: effective holdings rise from
<span class="num">6.0</span> (plain optimiser) to <span class="num">7.1</span>, without the wild swings.</p>
{{IMG:adv_bl.png|Current weights (red) vs the plain max-Sharpe optimiser (green) vs Black-Litterman (blue). BL's weights are smoother and less extreme — it won't bet the farm on a single noisy estimate.}}

<h3>2 — CVaR optimisation: minimise the fat tail, not the wobble</h3>
<p>Mean-variance treats an upside surprise and a crash as equally "risky." CVaR optimisation instead
minimises the <em>expected shortfall</em> — the average of your worst days — which is what you actually
fear. On your data it cuts the daily 95% shortfall from <span class="num">2.84%</span> (current) to
<span class="num">2.31%</span>, a shade below even the min-variance portfolio, while holding crypto under
8%. For a book with fat tails like yours (+3 kurtosis), this is the more honest objective.</p>
{{IMG:adv_cvar.png|Daily 95% expected shortfall (the average worst-day loss) for your current book, the min-variance portfolio, and the min-CVaR portfolio. CVaR optimisation targets the tail directly.}}

<h3>3 — Return attribution: where your +155% actually came from</h3>
<p>This splits your three-year return into each position's contribution, and then into
<em>allocation</em> (the decision to hold off-index assets like crypto) versus <em>selection</em> (your
equity picks beating the index). The verdict is striking: of your outperformance versus global stocks,
about <span class="num">+43%</span> came from selection and only <span class="num">+9%</span> from the
crypto allocation. <strong>Your edge is stock-picking, not the crypto bet</strong> — worth knowing
before you decide what to trim.</p>
{{IMG:adv_attribution.png|Each position's contribution to your total return (green positive, red negative). The Syfe fund, silver and a handful of single stocks did the heavy lifting.}}
<p class="small">Contributions use constant current weights, so they sum to roughly 124% rather than the
compounded 155% — the gap is the compounding of a moving book. Read the ranking, not the decimals.</p>

<h3>4 — Factor risk decomposition: what drives your volatility</h3>
<p>Stage 4 told you which factors drove your <em>returns</em>; this tells you which drive your
<em>risk</em>. Nearly half your volatility — <span class="num">47%</span> — is simply the market moving.
The style factors (size, value, momentum, quality) add another <span class="num">~16%</span>, and the
remaining <span class="num">37%</span> is stock-specific: the idiosyncratic bets you have chosen. So you
are roughly two-thirds "the market and styles" and one-third "your own picks."</p>
{{IMG:adv_factor_risk.png|Your portfolio variance split by source. The market factor dominates; about a third is stock-specific risk you could diversify away if you chose to.}}

<h3>5 — Fat-tailed & regime Monte Carlo: the honest crash</h3>
<p>Stage 5 rolled the dice assuming calm, normal days. Two more realistic engines: a <em>Student-t</em>
that fattens the daily tails, and a <em>regime-switching</em> model that spends 10% of its days in a
high-volatility "crisis." The surprise is that the Student-t looks almost identical to the normal over a
year — daily fat tails diversify away. The regime model does not: it pushes your bad-case (5th
percentile) year from <span class="num">−15%</span> to <span class="num">−28%</span>, and your chance of
a losing year from <span class="num">20%</span> to <span class="num">35%</span>. The lesson: it isn't fat
<em>daily</em> tails that hurt over a year — it's sustained crises.</p>
{{IMG:adv_montecarlo.png|Three one-year simulations. Normal (grey) and Student-t (blue) almost overlap; the regime-switching model (red) has a visibly heavier left tail — the realistic crash risk.}}

<h3>6 — Transaction costs & turnover: the edge, net of trading</h3>
<p>Every rebalance costs spread and fees, which the paper backtest ignores. Charging a sensible
per-class cost, moving to the optimised mixes costs only <span class="num">0.15–0.21%</span> one-off
(you are small and liquid), with a rough <span class="num">0.6–0.8%/yr</span> drag if you rebalanced
quarterly. Black-Litterman is the cheapest to implement (lowest turnover). The edge survives costs here —
but this is exactly how you would check whether a fancier strategy is worth the friction.</p>
{{IMG:adv_costs.png|Turnover (how much you would trade) and the rough annual cost drag for reaching each target portfolio. Black-Litterman moves the least.}}

<h3>7 — Liquidity & bespoke scenarios</h3>
<p>Two final desk checks. <strong>Liquidity:</strong> at 20% of daily volume, every single-name position
exits <em>same-day</em> — your positions are tiny next to how much trades, so you carry no liquidity
risk. <strong>Bespoke scenarios:</strong> beyond a generic market shock, tailored crises tell you more.
A US recession would cost about <span class="num">−$18k</span> (−36%), a crypto winter
<span class="num">−$7.8k</span>, and a 2008-style meltdown around <span class="num">−$25k</span> (−49%).
Stagflation is the mildest, because your silver actually helps. These are the numbers to make peace with
<em>before</em> they happen.</p>
{{IMG:adv_scenarios.png|Estimated portfolio loss under five tailored crises. The broad-equity events (recession, 2008-style) hurt most because most of your money is equity-like.}}

<div class="box you"><div class="h">The one-line summary of Stage 6</div>
Your edge is real and mostly stock-selection; your risk is mostly market beta with a fat,
regime-driven tail; you are fully liquid; and the optimiser's improvements survive trading costs.
Black-Litterman and CVaR are the two tools worth keeping in regular use.</div>

<h2 id="caveats">12. The honest caveats</h2>
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
<p>The Stage 6 methods carry their own assumptions, all editable in the notebook. The Black-Litterman
<em>views</em> are illustrative ones I chose to mirror your trim signals — change them and the answer
changes; that is the point of the model, not a flaw. The regime Monte Carlo uses a chosen crisis
frequency and severity (10% of days, 2.5× volatility); the transaction costs are per-class estimates in
basis points; and the bespoke scenarios are hand-set shocks, not forecasts. Treat them as a
well-structured way to ask "what if," with the inputs on the table for you to argue with.</p>

<h2 id="glossary">13. Glossary</h2>
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
<tr><td>Treynor ratio</td><td>Excess return per unit of market (beta) risk, not total risk.</td></tr>
<tr><td>Jensen's alpha</td><td>Return earned above what CAPM predicts for your beta.</td></tr>
<tr><td>Up / down capture</td><td>Your share of the benchmark's gains in up months vs its losses in down months.</td></tr>
<tr><td>Hit rate</td><td>The fraction of positions (or months) that are positive; a breadth check.</td></tr>
<tr><td>HHI</td><td>A concentration score; its reciprocal is the effective number of holdings.</td></tr>
<tr><td>Factor exposure</td><td>How much of your return is explained by common style bets.</td></tr>
<tr><td>Skewness</td><td>Whether returns lean toward big up-days (positive) or big down-days (negative).</td></tr>
<tr><td>Kurtosis (excess)</td><td>How fat the tails are; above 0 means extreme days are more common than a bell curve.</td></tr>
<tr><td>Omega ratio</td><td>Probability-weighted gains divided by losses around a threshold; above 1 is good.</td></tr>
<tr><td>Tail ratio</td><td>The size of your biggest up-moves versus your biggest down-moves.</td></tr>
<tr><td>M² (Modigliani)</td><td>Your Sharpe expressed as a return, priced at the benchmark's volatility, for a like-for-like compare.</td></tr>
<tr><td>Appraisal ratio</td><td>Factor-model alpha per unit of stock-specific risk; a measure of skill.</td></tr>
<tr><td>Cornish-Fisher VaR</td><td>A VaR adjusted for skew and fat tails, so it isn't fooled by the bell-curve assumption.</td></tr>
<tr><td>Drawdown duration</td><td>How long, not just how far, you stay below a previous peak.</td></tr>
<tr><td>Black-Litterman</td><td>A method that blends your own views with the market's implied returns for steadier optimisation.</td></tr>
<tr><td>CVaR optimisation</td><td>Optimising against the average tail loss instead of variance; better for fat-tailed books.</td></tr>
<tr><td>Equilibrium return</td><td>The return an asset must earn to justify its weight in a reference (market) portfolio.</td></tr>
<tr><td>View (Black-Litterman)</td><td>An explicit opinion you feed the model, e.g. "silver returns only 6%."</td></tr>
<tr><td>Return attribution</td><td>Splitting a return into the contribution of each holding, or allocation vs selection.</td></tr>
<tr><td>Allocation vs selection</td><td>Whether your edge came from what you held off-index, or from picking better names.</td></tr>
<tr><td>Factor risk decomposition</td><td>Splitting your volatility into market, style and stock-specific sources.</td></tr>
<tr><td>Regime-switching</td><td>A model that alternates between calm and crisis states; captures crashes a normal model misses.</td></tr>
<tr><td>Turnover</td><td>How much of the portfolio you trade to reach a target; drives transaction costs.</td></tr>
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
