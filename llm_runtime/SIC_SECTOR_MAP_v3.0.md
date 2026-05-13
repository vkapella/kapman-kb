---
system: KapMan
doc_type: reference
kb_version: 3.0.0-alpha
file_last_updated: 2026-05-13
status: draft
tier: T3
---

# SIC SECTOR MAP

This file is a lookup table only. It maps SIC code ranges to sector labels and benchmark ETFs used for relative-strength and regime context in screening. No behavioral rules, heuristics, or principles are expressed here; those belong to T0–T2 files.

## Mapping table

| SIC Range | Description | Sector | Benchmark ETF |
|---|---|---|---|
| 1000–1099 | Metal Mining | Materials | XLB |
| 1200–1299 | Coal Mining | Energy | XLE |
| 1300–1399 | Oil & Gas Extraction | Energy | XLE |
| 1400–1499 | Nonmetallic Minerals | Materials | XLB |
| 2000–2099 | Food & Kindred Products | Consumer Staples | XLP |
| 2100–2199 | Tobacco Products | Consumer Staples | XLP |
| 2200–2299 | Textile Mill Products | Industrials | XLI |
| 2300–2399 | Apparel & Footwear | Consumer Discretionary | XLY |
| 2400–2499 | Lumber & Wood | Industrials | XLI |
| 2500–2599 | Furniture & Fixtures | Industrials | XLI |
| 2600–2699 | Paper & Products | Materials | XLB |
| 2700–2799 | Printing & Publishing | Industrials | XLI |
| 2800–2899 | Chemicals & Allied | Materials | XLB |
| 2900–2999 | Petroleum Refining | Energy | XLE |
| 3000–3099 | Rubber & Plastics | Industrials | XLI |
| 3100–3199 | Leather | Consumer Discretionary | XLY |
| 3200–3299 | Stone, Clay, Glass | Materials | XLB |
| 3300–3399 | Primary Metal Industries | Materials | XLB |
| 3400–3499 | Fabricated Metal | Industrials | XLI |
| 3500–3599 | Machinery (non-electrical) | Industrials | XLI |
| 3600–3699 | Electrical Equipment | Industrials | XLI |
| 3674 | Semiconductors ¹ | Information Technology | XLK |
| 3700–3799 | Transportation Equipment | Industrials | XLI |
| 4000–4099 | Railroad Transportation | Industrials | XLI |
| 4100–4199 | Trucking & Motor Freight | Industrials | XLI |
| 4200–4299 | Water Transportation | Industrials | XLI |
| 4300–4399 | Air Transportation | Industrials | XLI |
| 4400–4499 | Pipeline Transportation | Energy | XLE |
| 4600–4699 | Pipelines (NEC) | Energy | XLE |
| 4700–4799 | Transportation Services | Industrials | XLI |
| 4800–4899 | Communications | Communication Services | XLC |
| 4900–4999 | Electric, Gas, Water Utilities | Utilities | XLU |
| 5000–5999 | Wholesale Trade | Industrials | XLI |
| 5300–5399 | Retail — General Merchandise | Consumer Discretionary | XLY |
| 5400–5499 | Retail — Food | Consumer Staples | XLP |
| 5500–5599 | Retail — Motor Vehicles | Consumer Discretionary | XLY |
| 5600–5699 | Retail — Apparel | Consumer Discretionary | XLY |
| 5700–5799 | Retail — Home & Furniture | Consumer Discretionary | XLY |
| 5800–5899 | Eating & Drinking Places | Consumer Discretionary | XLY |
| 5900–5999 | Retail — Miscellaneous | Consumer Discretionary | XLY |
| 6000–6099 | Depository Institutions | Financials | XLF |
| 6100–6199 | Non-Depository Institutions | Financials | XLF |
| 6200–6299 | Security Brokers & Dealers | Financials | XLF |
| 6300–6399 | Insurance Carriers | Financials | XLF |
| 6400–6499 | Insurance Agents & Brokers | Financials | XLF |
| 6500–6599 | Real Estate | Real Estate | XLRE |
| 6700–6799 | Holding & Investment Companies | Financials | XLF |
| 6798 | REITs ¹ | Real Estate | XLRE |
| 7000–7099 | Hotels & Lodging | Consumer Discretionary | XLY |
| 7200–7299 | Personal Services | Consumer Discretionary | XLY |
| 7300–7399 | Business Services | Industrials | XLI |
| 7370–7379 | Computer Software & Services ¹ | Information Technology | XLK |
| 7381 | Detective & Protective Services ¹ | Industrials | XLI |
| 7500–7599 | Auto Repair & Services | Consumer Discretionary | XLY |
| 7600–7699 | Miscellaneous Repair Services | Consumer Discretionary | XLY |
| 7700–7799 | Motion Picture & Video | Communication Services | XLC |
| 7900–7999 | Amusement & Recreation | Consumer Discretionary | XLY |
| 8000–8099 | Offices of Physicians | Health Care | XLV |
| 8100–8199 | Dentists | Health Care | XLV |
| 8200–8299 | Hospitals | Health Care | XLV |
| 8300–8399 | Medical & Dental Labs | Health Care | XLV |
| 8400–8499 | Medical Services & Allied | Health Care | XLV |
| 8500–8599 | Nursing & Personal Care | Health Care | XLV |
| 8600–8699 | Hospital & Medical Services | Health Care | XLV |
| 8700–8799 | Engineering & Research | Industrials | XLI |
| 8800–8999 | Services, NEC | Industrials | XLI |
| 9000–9999 | Government & Public Administration | N/A | — |

*¹ Point-code or sub-range that overrides the parent range classification.*

## Legacy anchors (for legend citations and back-compat)

No named rule IDs from v2.3 archive map to this file. The v2.3 antecedent (`SIC_SECTOR_ETF_MAPPING_v2.3.md`) carried no legacy rule IDs; it was a data table with no behavioral anchors.
