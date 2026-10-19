# AirConnect India v2.0 Engineering Plan

## Purpose and scope

The project must remain a small, offline university laboratory application while making its data processing, model selection, numerical claims, and submission artifacts reproducible. Python prepares all data and results; the browser only reads precomputed assets. No authentication, server database, cloud runtime, or front-end framework is required.

## Functional requirements

1. Validate pinned domestic monthly, annual domestic/international, and quarterly international source tables.
2. Build exact-calendar lag and rolling features without converting absent observations to zero.
3. Compare regression candidates and naive baselines on identical chronological observations.
4. Train a defensible binary growth classifier and publish its actual confusion counts.
5. Evaluate K-Means for k = 2–6 and use PCA to visualise a multi-feature airport space.
6. Export one canonical JSON artifact consumed by the website, charts, report, and presentation.
7. Preserve four website sections with accessible filters, maps, tables, charts, sub-tabs, and CSV export.
8. Produce editable DOCX and PPTX outputs plus current PDF exports.

## Nonfunctional requirements

- Deterministic seed 37 for stochastic estimators.
- Complete offline demonstration after generated assets are packaged.
- UTF-8 and LF-stable generated text.
- WCAG 2.2 AA-oriented keyboard interaction, visible focus, accessible chart labels, data tables, reduced motion, and viewport-aware tooltips.
- No unsupported performance, capacity-utilisation, or route-policy claims.
- CI runtime appropriate for a small assignment.

## Architecture

```text
Pinned DGCA-derived CSVs
          |
          v
schema, key, range and reconciliation checks
          |
          v
exact-calendar airport-month feature panel
          |
          +--> chronological regression and classification
          |
          +--> annual multifeature K-Means and PCA
          |
          v
data/processed/analysis.json
     |          |           |
     v          v           v
offline site   figures   report and deck
```

## Data workflow

The unmodified upstream files are stored under `data/external/india-aviation-stats/` with licence, source commit, and SHA-256 fingerprints. Validation checks exact schemas, unique keys, period ranges, nonnegative passenger values, `passengers = departures + arrivals`, and complete-year monthly-to-annual domestic reconciliation.

Feature construction uses exact month offsets. For example, lag 12 for airport A in March 2025 is joined only from airport A in March 2024. If that source row is absent, the lag remains missing. Rolling means use pre-target lag columns. Targets are never imputed. Numeric preprocessing and categorical encoding are fitted separately inside every training fold.

## ML workflow

Regression and classification use expanding validation folds with 2022, 2023, and 2024 as validation years. The 2025 period remains untouched until the selected configuration is fixed. Candidate grids are deliberately bounded. Regression selection minimises mean validation MAE; classification selection maximises mean validation balanced accuracy.

The one-step-ahead setting assumes the previous month's actual observation is available. Longer recursive forecasting is not evaluated and must not be inferred from the results.

K-Means uses six features: log domestic volume, log international volume, domestic annual growth, monthly seasonality coefficient of variation, international share, and active months. Candidate k values require a minimum cluster size of five. Within 0.02 of the best viable silhouette, the smaller k is preferred for interpretability.

## Acceptance criteria

- Source files and hashes are present and validated.
- No target or post-target field appears among predictive features.
- All regression methods use 1,357 common 2025 rows.
- Regression metrics independently recalculate from exported predictions.
- Classification confusion counts total 1,357 and reproduce reported metrics.
- Cluster counts total 129; PCA has two components and six loadings.
- Website functions offline with no CDN request.
- Desktop, tablet, and mobile views have no horizontal overflow outside intentional chart/table scroll regions.
- DOCX, PPTX, and PDFs render without overlap or clipping.
- Automated tests pass, or a failure and its cause are recorded.

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| Pandemic distribution shift | Preserve chronological folds and discuss 2020–2022 instability |
| Strong autocorrelation | Compare directly with previous-month and seasonal naive forecasts |
| Large-airport error dominance | Report WAPE, median AE, and traffic-size segments |
| Missing airport-months | Exact joins, missing indicators, train-only imputation |
| Upstream revisions | Pin commit and checksums; preserve unmodified files |
| Classification imbalance | Balanced accuracy, per-positive precision/recall/F1, ROC and PR analysis |
| Degenerate clusters | Minimum-size rule plus silhouette and inertia review |
| Stale submission artifacts | Generate figures and documents from canonical analysis JSON |

## Implementation map

- `src/pipeline.py`: validation and feature construction.
- `src/modeling.py`: tuning, evaluation, clustering, and PCA.
- `src/build.py`: canonical result export.
- `src/build_charts.py`: numerical figures.
- `src/build_documents.py`: academic outputs.
- `site/`: dependency-free presentation layer.
- `tests/`: data, leakage, metric, structure, and browser checks.
