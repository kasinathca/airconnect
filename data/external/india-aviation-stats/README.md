# Pinned external dataset

These files were downloaded without modification from `mkubicek/india-aviation-stats` at commit `bce8fc78f2be1de88154c1d8e62d13ffc0d8e171` on 19 October 2026.

| File | Grain | Rows | Coverage | SHA-256 |
|---|---|---:|---|---|
| `airport_monthly.csv` | Domestic airport × month | 13,599 | 2015–2026 | `ecc5a9862ced44d3d9acf224559e135cfabc3ce2910c6a132e76b63e37bb1122` |
| `airport_yearly.csv` | Airport × year × category | 1,388 | 2015–2025 | `65f5092ea041b1833b17186eabee7cf913ec7ec99317dafa159a92b2e0a27674` |
| `airport_international_quarterly.csv` | International airport × quarter | 1,248 | 2015–2026 | `8f27dca8d4ead4e2aa52a5d6103a02d80d57b72a615327a324008f025794fae7` |

The upstream project describes passengers as departures plus arrivals. The pipeline verifies this identity, unique keys, valid periods, nonnegative values, and reconciliation of complete domestic years with the annual table. The upstream MIT licence is preserved in this directory.

The source repository reports that early 2015 and current 2026 coverage are partial. AirConnect v2.0 excludes partial 2026 from modelling and requires exact calendar lags; absent months are not converted to zero.
