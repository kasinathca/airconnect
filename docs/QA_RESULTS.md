# AirConnect India v2.0 Quality Assurance Results

## Baseline record

The untouched v1.0 baseline was tested before ML modification. Three tests passed and two failed: generated JavaScript changed LF line endings to CRLF on Windows, and one HTML test used the cp1252 default to read UTF-8 content. Baseline commit: `0e35485ef825af340093a8943166e67a8c633637`.

## Data verification

- `airport_monthly.csv`: 13,599 rows, 144 airports, 2015–2026, zero duplicate keys, zero missing core values, zero negative passenger counts.
- `airport_yearly.csv`: 1,388 rows, 140 airports, 2015–2025, zero duplicate keys.
- `airport_international_quarterly.csv`: 1,248 rows, 35 airports, 2015–2026, zero duplicate keys.
- Monthly and quarterly passenger values equal departures plus arrivals.
- Complete domestic years reconcile between monthly and annual tables.
- Upstream commit and file hashes are saved in the canonical artifact.

## ML verification

- Exact-calendar lag checks compare sampled generated lags with independent source lookups.
- Predictive feature lists contain no target field.
- Expanding validation years are 2022, 2023, and 2024; 2025 is held out.
- All regression candidates and baselines use the same 1,357 test observations.
- Exported Random Forest predictions independently reproduce MAE 17,479.31, RMSE 50,429.53, and R² 0.9939 within rounding tolerance.
- Classifier confusion matrices each sum to 1,357; the selected Logistic Regression matrix is TN 688, FP 81, FN 196, TP 392.
- Four selected clusters sum to 129 airports.
- PCA includes 129 points, six feature loadings, and valid explained variance ratios.

## Website verification checklist

- Four primary navigation sections.
- Regression, Classification, and Clustering/PCA sub-tabs.
- Airport year, group, and search filters.
- Map marker keyboard activation.
- CSV export.
- Custom mouse, keyboard, and touch tooltips with Escape dismissal.
- Chart text alternatives and numeric result tables.
- Offline local assets only; no CDN, analytics, or remote runtime dependency.
- All six offline pytest checks pass.
- Built-in Chromium smoke check verified all four primary sections, all three ML sub-tabs, the regression table, 688/81/196/392 confusion counts, PCA content, and an empty browser error/warning log.
- A 390 × 844 responsive check retained the ML heading, tabs, and PCA content with no horizontal document overflow.

## Document verification checklist

- Markdown report, editable Word report, and PDF contain consistent source dates, sample counts, model names, and metrics.
- Editable PowerPoint and PDF deck contain 15 slides.
- Charts and diagrams are regenerated from `analysis.json`.
- DOCX pages and PDF pages are rendered to PNG and visually inspected.
- Presentation slides are rendered and checked for overlap, clipping, and unreadable legends.

## Known limitations

- The previous-month baseline remains slightly more accurate than the selected Random Forest on 2025 MAE.
- The validation-selected Logistic Regression is not the highest-scoring classifier on the final test; the Random Forest classifier is shown as a post-selection comparison, not retroactively selected.
- 2026 source data are partial and excluded from training and evaluation.
- Coordinate coverage is incomplete for some IATA codes; those records remain in tables.
