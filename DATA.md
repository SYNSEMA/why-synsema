# Data sources

| File | Case | Origin | How it was produced |
| --- | --- | --- | --- |
| `cases/01-mcp-servers/data/catalog.json` | 1 | Synthetic, fictional companies | `data/generate_catalog.py`, seed 11 |
| `cases/04-invoice-approval/data/invoices.json` | 4 | Synthetic, fictional companies | `data/generate_invoices.py`, seed 21 |
| `cases/02-llm-written-analytics/data/books.csv` | 2 | [books.toscrape.com](https://books.toscrape.com), a sandbox site built for scraping practice | Scraped catalog (1,000 books), October 2026 |
| `cases/02-llm-written-analytics/data/weather_summary.csv` | 2 | [Open-Meteo](https://open-meteo.com) historical API (CC BY 4.0) | Hourly 2025 data for 40 cities, aggregated per city |
| `cases/02-llm-written-analytics/data/game_prices.csv` | 2 | [CheapShark](https://www.cheapshark.com) API | Prices of 40 games across ~35 stores, October 2026 |
| `cases/02-llm-written-analytics/data/steam_regional_prices.csv` | 2 | Steam store `appdetails` API + [open.er-api.com](https://www.exchangerate-api.com) exchange rates | Prices in 7 countries converted to USD |
| `cases/02-llm-written-analytics/data/taxi_*.parquet` | 2 | [NYC TLC Trip Record Data](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page), yellow taxis, Aug 2025 to Jul 2026 | 44.3 M trips aggregated by hour × borough, top 50 routes and month |
| `cases/02-llm-written-analytics/data/demand_validation.csv` | 2 | Derived from the NYC TLC data + Open-Meteo | Daily demand model, last 4 weeks of validation |
| `cases/02-llm-written-analytics/data/trades.jsonl` | 2 | Coinbase and Binance public WebSocket feeds | 60 seconds of BTC, ETH and SOL trades, October 2026 |
| `cases/02-llm-written-analytics/data/teacher_labels.csv` · `cases/05-ai-act-traceability/data/teacher_labels.csv` | 2, 5 | Book titles above, labeled by Jev (TypeSafe) with LLM review of low-confidence ones | Genre labels with the true category for comparison |
| `cases/05-ai-act-traceability/data/extra_data.csv` | 5 | 80 titles from the same catalog | The "undocumented" extra data used to test traceability |

Open-Meteo data is used under CC BY 4.0 (Open-Meteo.com). NYC TLC data is public. The scraped and API data are small aggregates used for measurement only.
