# Changelog

All notable changes to edgar13f. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/); versions follow semver
(pre-1.0: minor bumps may include breaking changes).

## [0.7.0] - 2026-07-17

### Added
- **Form 4 insider transactions** (`form4.py`): CLI `edgar13f insiders
  AAPL`, `/api/insiders/<symbol>`, MCP tool
  `get_insider_transactions`, and an INSIDER TRANSACTIONS dashboard
  block. Non-derivative rows only; open-market purchases (P) and
  sales (S) are flagged as the signal. Parsed filings are disk-cached
  by accession number like 13F holdings.
- **13F position history**: CLI `edgar13f history buffett AAPL`,
  `/api/position-history/<manager>/<query>`, MCP tool
  `get_position_history`, and a 13F POSITION HISTORY dashboard block
  with per-quarter value bars - one manager's stake in one name across
  N quarters. Query by ticker, CUSIP, or issuer-name substring.
- **10 new tracked managers** (now 14): Tepper/Appaloosa, Klarman/
  Baupost, Loeb/Third Point, Dalio/Bridgewater, Druckenmiller/
  Duquesne, Marks/Oaktree, Li Lu/Himalaya, Einhorn/DME (Greenlight's
  successor filer), Fundsmith, Tiger Global. Every CIK verified live
  against a current (Q1 2026) 13F-HR.
- **Name-based ticker fallback**: CUSIPs OpenFIGI's keyless tier can't
  map (e.g. Chubb's H1467J104) now resolve by matching the 13F issuer
  name against SEC's `company_tickers.json`; learned mappings persist
  in the resolver's disk cache.

### Fixed
- `search_company_cik` now handles EDGAR's exact-match redirect (the
  single-company filing-list page), which previously parsed as garbage
  `{"name": "Documents", "cik": None}` rows.

## [0.6.0] - 2026-07-07 and earlier

Pre-changelog history - see `HANDOVER.md` for the session-by-session
record. Highlights: 13F client/CLI (search, holdings, diff, consensus,
holders), Bloomberg-style web dashboard with customizable widget tabs,
vendored KLineChart (Apache-2.0) charting with indicators + drawing,
quotes/world markets (Yahoo v8), SEC XBRL fundamentals, screener, news
(7 RSS feeds), corporate events, Treasury/BLS/FRED macro, portfolio
risk, options (experimental), MCP server, Docker, GitHub Actions CI.
