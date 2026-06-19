// Curated, static context for the dashboard. Keyed by the `ticker` field in latest.json.
// Fund-ETF blurbs reuse Syfe's own one-liners from the Core Equity100 composition screen.

export const CLASS_BLURB = {
  equity: 'Individual company shares — your direct single-stock picks.',
  etf: 'Exchange-traded funds — baskets that track an index, sector, or commodity.',
  crypto: 'Cryptocurrencies — digital assets; expect high volatility.',
  cash: 'Uninvested cash.',
}

const TICKER_DESC = {
  // --- Direct equities ---
  ORCL: 'Enterprise database & cloud-infrastructure giant; now a major AI-capacity provider.',
  MSTR: 'Software firm turned leveraged Bitcoin holding vehicle.',
  TMC: 'Deep-sea explorer targeting seabed battery metals; pre-revenue, speculative.',
  SPCX: 'SpaceX — rockets and the Starlink satellite-internet network.',
  CEG: 'Largest US nuclear power generator; a key AI-data-centre energy play.',
  QBTS: 'Quantum-computing hardware (annealing); early-stage, speculative.',
  IONQ: 'Trapped-ion quantum-computing pure-play; early-stage, speculative.',
  MUFG: "Japan's largest bank (megabank group).",
  NNDM: 'Additive manufacturing for printed electronics; speculative micro-cap.',
  ORGN: 'Carbon-negative materials / bioplastics; speculative micro-cap.',
  BZ: "China's largest online recruitment platform (BOSS Zhipin).",

  // --- Direct ETFs ---
  VWO: 'Broad emerging-markets equities (Vanguard).',
  SLV: 'Tracks the spot price of physical silver.',

  // --- Crypto (keyed by CoinGecko id) ---
  bitcoin: 'The original cryptocurrency; digital store of value.',
  ethereum: 'Leading smart-contract blockchain.',
  'crypto-com-chain': "Crypto.com's exchange utility token (Cronos).",
  solana: 'High-throughput layer-1 blockchain.',
  polkadot: 'Multi-chain interoperability protocol.',
  ripple: 'Token for fast, low-cost cross-border payments (XRP).',

  // --- Syfe Core Equity100 constituents (Syfe's own descriptions) ---
  'CSPX.L': 'The 500+ biggest US companies, market-cap weighted (S&P 500).',
  EFA: 'Developed-market equities outside the US & Canada — Nestlé, Roche, Novartis.',
  QQQ: 'The 100 largest non-financial Nasdaq names — Microsoft, Apple, Google.',
  'XDEW.L': 'The S&P 500 equally weighted — less top-heavy than the standard index.',
  DUHP: 'Large US companies screened for high profitability (Dimensional).',
  'EIMI.L': '3000+ emerging-market companies — TSMC, Tencent, Samsung, Alibaba.',
  DFAT: '1400+ US small/mid-caps tilted to value & profitability (Dimensional).',
  MOAT: 'Fairly-priced companies with durable competitive advantages (wide moats).',
  MCHI: 'Large & mid-cap China equities — JD.com, Ping An.',
  KWEB: 'China internet companies — Tencent, Meituan, Alibaba.',
  'cash-sgd': 'Uninvested cash balance in the fund.',
}

export function getDesc(ticker) {
  return TICKER_DESC[ticker] || ''
}
