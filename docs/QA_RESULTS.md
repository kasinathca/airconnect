# Validation summary — 19 October 2026

## Tests and review gates

| Gate | Status | Evidence |
|---|---|---|
| CSV source validity | PASS | 614 source rows; no duplicate year-airport-category keys; all counts nonnegative |
| National category totals | PASS | 2022–2025 source sum equality for domestic/international categories |
| Deterministic ML | PASS | Fixed seed; regenerated `data.js` identical byte-for-byte |
| Model coherence | PASS | 129 clustering airports; 116 chronological test predictions; evaluation metrics recomputed |
| Python unit suite | PASS | 5 tests passed |
| Desktop Chromium | PASS | 1440×900 browser; 4 pages, chart and map, search, year switching, table pagination |
| Mobile Chromium | PASS | 390×844 browser; 4 pages, no horizontal document overflow |
| JavaScript runtime | PASS | Zero page errors across tested views |
| Word report | PASS | DOCX converted into a 6-page PDF for visual inspection |
| Presentation | PASS | 10 PPTX slides converted to a 10-page PDF for visual inspection |
| Runtime network independence | PASS by architecture | No external JS library/CDN/API requests in the application; all model results embedded |

## Interpretation checkpoints

- 2025 K-Means: n=129; k=3; Silhouette=0.6235337.
- 2025 Random Forest holdout: MAE=451,551.93; RMSE=2,044,383.36; R²=0.9282.
- 2025 prior-year baseline: MAE=182,476.34; RMSE=354,819.58; R²=0.9978.
- The baseline wins. The website and documents state this clearly.

## Unverified environments and non-goals

- The project was not executed on the user's own Windows installation; the built-in batch launcher is straightforward but actual machine-specific security policies can differ.
- No accessibility certification (e.g. full WCAG audit) or formal usability study was performed.
- External data sources are cited; re-downloading the full DGCA upstream workbooks is not part of the offline reproduction path.
- No model is deployed as a prediction API; the HTML viewer presents reproducibly generated historical test results.
