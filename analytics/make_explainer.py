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
<li><a href="#mc">Stage 5: Monte Carlo, your year ahead in 10,000 futures</a></li>
<li><a href="#verdict">What it all means, and what to consider doing</a></li>
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
<p>Here is the plain-English "so what" for each measure, then a short list of options your numbers
point to. None of this is advice; it is what the analysis suggests, and the decisions are yours.</p>
<h3>What each number implies for you</h3>
<table><thead><tr><th>Measure</th><th>Your number</th><th>What it means for you</th></tr></thead><tbody>
<tr><td>Sharpe ratio</td><td>0.76 (0.90 reachable)</td><td>A fair reward for your risk, but you are leaving some on the table; the same risk could earn more.</td></tr>
<tr><td>Sortino ratio</td><td>2.19</td><td>Much of your "risk" is upside surprise, not real pain. Your downside is well paid.</td></tr>
<tr><td>Max drawdown / Calmar</td><td>−18% / 1.91</td><td>Be ready to see the book ~18% below a peak, maybe more ahead. The reward for that pain is healthy.</td></tr>
<tr><td>VaR 99%, one day</td><td>−$1,650</td><td>On a 1-in-100 bad day you could drop about $1,650. Make sure that never forces a panic sale.</td></tr>
<tr><td>Expected Shortfall 99%</td><td>−$2,370</td><td>When a bad day does land, the average is worse than VaR alone. The tail bites harder than it looks.</td></tr>
<tr><td>Beta vs world stocks</td><td>1.09</td><td>You fall slightly more than global equities in a sell-off, not less.</td></tr>
<tr><td>Tracking error</td><td>13.1%</td><td>You stray a long way from a plain index. You are making active bets, for better or worse.</td></tr>
<tr><td>Information ratio</td><td>1.02</td><td>Those bets paid off over the window. That is history, not a promise.</td></tr>
<tr><td>Concentration (HHI)</td><td>3.1 (12.1 look-through)</td><td>The real concentration is half your money in one product. The fund diversifies inside, so the fix is to not let it grow, not to panic.</td></tr>
<tr><td>Factor tilt</td><td>small-cap, low quality</td><td>You are making a speculative bet. In a flight to safety this profile tends to lag.</td></tr>
<tr><td>Equity −20% stress</td><td>−$8,800</td><td>A normal-sized bad market costs you roughly this. Size positions so it does not derail your plan.</td></tr>
<tr><td>Monte Carlo chance of loss</td><td>~20% (bad case −$7,900)</td><td>About a 1-in-5 chance of a down year. Decide now whether you can sit through that calmly.</td></tr>
</tbody></table>

<h3>Options the analysis points to</h3>
<p>Three independent methods, the optimiser, the risk decomposition, and the simulation, agree on the
same handful of moves. In rough priority:</p>
<ol>
<li>Trim your two biggest risk hogs, Bitcoin and silver. Stage 3 shows both use more of your risk
budget than they return. They are the clearest "too much risk for the reward" positions.</li>
<li>Shrink the crypto sleeve. You hold about 16%; the optimiser wants nearer 3%, and the six coins are
so correlated (the red block in the heatmap) that they behave like one bet, not six.</li>
<li>Do not let the Syfe fund grow past a level you are comfortable with. At 53% it is a single-product
dependence. It is a good, efficient holding, so this is about concentration, not quality.</li>
<li>Add the cheap diversifiers the optimiser favours: emerging markets (VWO), the Japanese bank (MUFG),
and some higher-quality names. They lift your Sharpe and soften the speculative, low-quality tilt.</li>
<li>Match the risk to your stomach. The simulation puts roughly a 1-in-5 chance on a down year and a
−$8,000 bad case. If that is fine, your aggressive book is a coherent bet that the boom continues. If
it is not, move toward the optimised mix, which trades a little expected return for far fewer bad
years.</li>
</ol>
<div class="box warn"><div class="h">The honest tension, and a disclaimer</div>
Over the last three years your riskier current book (+155%) beat the optimised one (+123%), because the
optimiser trims exactly the crypto and silver that soared. The optimiser lowers risk; it does not
promise higher returns. So the real decision is your own view on whether the next few years reward risk
the way the last few did. And to be clear: this is analysis, not financial advice. I am not a licensed
adviser, and every decision here is yours to make.</div>

<h2 id="caveats">8. The honest caveats</h2>
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

<h2 id="glossary">9. Glossary</h2>
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
