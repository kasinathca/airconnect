# Source data provenance

**Traffic table:** https://github.com/mkubicek/india-aviation-stats — `data/processed/airport_yearly.csv` (MIT). Input data from DGCA workbooks cleaned and normalised by the upstream project. The complete 2022–2025 rows with three-character IATA codes are included in `airport_yearly_2022_2025.csv`; 2016–2025 domestic/international category aggregates are included in `national_2016_2025.csv`. The year 2015 is excluded from this total-traffic series because the upstream annual table does not contain domestic rows that year.

The raw annual table was read and transcribed using exact integer preservation and a reversible base36 compression in `src/seed_data.py`. Re-running that script reproduces the bundled CSV. Validation checks match all four 2022–2025 annual category sums exactly; source rows also are unique by year, airport, category.

**Geographic coordinates:** https://github.com/brandonhimpfen/airports — `data/airports.csv` (MIT). Coordinates matched on IATA code and latitude/longitude plausibility; available for 93/129 domestic-reporting airports in 2025. These coordinates are only for approximate visual positioning, not statistical inference.

**Public infrastructure headline figures:** Ministry of Civil Aviation, 74 facilities in 2014 and 165 operational facilities on 7 July 2026. Not interchangeable with DGCA traffic-reporting airport counts.

**Map vector outline:** Natural Earth low-resolution India polygon, public domain. Simplified, precomputed JavaScript path (`site/assets/india-map.js`). It is an illustrative geographic outline, not a statement of borders or detailed administrative boundaries.
