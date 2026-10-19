# Changelog

## 2.0.0 — 19 October 2026

- Pinned and validated 13,599 upstream domestic airport-month rows plus annual and international quarterly tables.
- Replaced the small annual regression task with leakage-safe one-step airport-month forecasting and expanding chronological validation.
- Added Ridge, CART, Random Forest, and Histogram Gradient Boosting comparisons with three naive baselines.
- Added a legitimate 10% year-on-year growth classifier with real confusion matrix, ROC, and precision-recall data.
- Expanded K-Means to six airport features, evaluated k = 2–6, and added PCA.
- Rebuilt the offline website with ML sub-tabs, accessible tooltips, interactive SVG charts, and result tables.
- Added publication charts, a revised report and presentation workflow, stronger automated tests, and GitHub Actions CI.
- Retained the previous-month naive method as the strongest 2025 MAE result; no unsupported model-win claim is made.

## 1.0.0 — 19 October 2026

- Defined functional requirements, architecture, data provenance and validation gates.
- Added verified real aviation traffic records for 2022–2025 and annual national totals for 2016–2025.
- Implemented K-Means clustering, Random Forest regression and chronological persistence-baseline comparison.
- Built standalone offline website with responsive Microsoft Fluent-inspired academic interface.
- Added year and group filters, airport search, local vector India map, contextual tooltips, accessible controls, charting and CSV export.
- Added reproducible Python training pipeline, unit tests, report in Word/PDF, presentation in PPTX/PDF and presentation notes.
- Completed headless Chromium desktop/mobile interaction tests and desktop document layout verification.
