# Data Sources — Where to Find Credible Industry Data

Triangulate every material number from **≥2 independent sources** and record source + date.
Prefer primary sources over secondary summaries. Mark anything you can't corroborate as
*[unverified]*.

## Source hierarchy (most → least reliable)
1. **Primary filings & regulators** — company annual reports / 10-K / 20-F / 招股书(prospectus),
   regulator data (SEC, CSRC, central banks).
2. **Official statistics** — national statistical bureaus, customs/trade data, ministry data.
3. **Industry associations & standards bodies** — membership data, shipment/capacity stats.
4. **Specialist trade press & research houses** — sector journals, market-research firms
   (cite the figure + the firm + the date; note if paywalled/estimate).
5. **Sell-side & general press** — useful for narrative and consensus; verify the underlying number.

## Global
- Company filings: SEC EDGAR, company IR pages, annual reports.
- Macro/market: World Bank, IMF, OECD, UN Comtrade (trade flows), national statistics offices.
- Industry: trade associations for the specific sector; standards bodies; patent offices
  (USPTO/EPO/WIPO) for innovation/IP signals.
- Markets: exchange filings, earnings-call transcripts, investor-day decks.

## China (中国数据源)
- 国家统计局 (NBS), 海关总署 (customs/进出口), 工信部 / 发改委 / 各部委公开数据.
- 上市公司年报 / 招股说明书 (巨潮资讯网 cninfo, 交易所披露).
- 行业协会 (e.g. 中国半导体行业协会、各产业联盟) 的出货/产能数据.
- 行业研究: 券商研报、专业咨询机构、行业垂直媒体 (verify the number, note if it's an estimate).

## How to use the tools in this skill
- `WebSearch` to find candidate sources; then `web_fetch` the actual page to read the number
  in context (don't trust a search snippet alone).
- If a page is client-rendered / returns a shell, escalate to the Chrome tools to render it.
- If connected data MCPs exist (financial data, internal DBs), prefer them for hard numbers.

## Citation format
For each material claim keep: **Title — Publisher/Source — Date — URL**. Compile these into
the report's Sources section. Date matters: an industry figure without a year is unusable.

## Red flags
- A number that appears everywhere but traces back to one original (false triangulation).
- "Market expected to reach $X by 20YY at Z% CAGR" with no methodology — treat as marketing.
- Mixing definitions (revenue vs. shipments vs. installed base) across sources — normalize first.
