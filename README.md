# 🐋 WhaleWatch

> Track political trades, hedge fund moves, and government contract flows — globally.

**Live app → [572kgdy8rm-max.github.io/whalewatch](https://572kgdy8rm-max.github.io/whalewatch/)**

-----

## What it does

WhaleWatch surfaces high-signal trading activity from two sources most retail investors ignore:

- **Politicians** — Congressional, Senate, and international legislative disclosure filings (STOCK Act, Register of Members Interests, EU Parliament, NPC/CPPCC, LegCo)
- **Hedge Funds** — 13F filings, Tiger Cub tracker, activist fund moves

Then cross-references with:

- **Contract Watch** — Political donation → government contract timelines (FEC.gov + USASpending.gov)
- **Backtest Engine** — Historical signal accuracy and simulated portfolio performance

-----

## Features

|Feature           |Description                                          |
|------------------|-----------------------------------------------------|
|🏆 Top 10          |Global highest-conviction picks with whale confluence|
|📊 Backtest        |Signal accuracy engine + simulated equity curve      |
|🤝 Contracts       |Donation-to-contract flow tracker                    |
|🇺🇸🇦🇺🇪🇺🇨🇳🇭🇰 Markets     |Per-country politician + fund tabs                   |
|📈 Yahoo Finance   |Direct link to live quote from every card            |
|📌 Personal Tracker|Mark signals you follow — localStorage persisted     |
|⬇ Export          |Download all signal data as JSON                     |

-----

## Backtest disclaimer

> All backtest returns are **simulated** from recorded historical signal outcome strings — not actual trade execution prices, bid/ask spreads, slippage, or fees. Past signal accuracy does not guarantee future results.

-----

## Data sources

- [STOCK Act filings](https://efts.house.gov/LATEST/search-index?q=&dateRange=custom&fromDate=2024-01-01&toDate=2026-06-01&type=fd) — US Congressional disclosures
- [SEC EDGAR 13F](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&type=13F) — Hedge fund quarterly holdings
- [FEC.gov](https://www.fec.gov/data/) — Political donations
- [OpenSecrets.org](https://www.opensecrets.org/) — Donor-to-contractor analysis
- [USASpending.gov](https://www.usaspending.gov/) — Federal contract awards
- EU Parliament transparency register
- Hong Kong LegCo interests register
- NPC/CPPCC public filings (China)

-----

## Setup

No build step. Pure HTML + React 18 (CDN).

```bash
git clone https://github.com/572kgdy8rm-max/whalewatch.git
cd whalewatch
open index.html   # runs locally in any browser
```

GitHub Pages deploys automatically on push to `main` via `.github/workflows/deploy.yml`.

-----

## ⚠ Disclaimer

This is not financial advice. Signal data is for informational and research purposes only. Some trade filings are unverified — verification notes are shown inline where applicable. Always verify disclosures at primary sources before making investment decisions.
