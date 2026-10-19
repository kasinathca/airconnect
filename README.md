# AirConnect India

AirConnect India v2.0 is a reproducible, offline MDI4001 Machine Learning for Data Science project about Indian airport passenger traffic. It combines validated DGCA-derived data, chronological forecasting, supervised classification, K-Means clustering, PCA, and a static academic website.

## Headline result

The redesigned airport-month pipeline reduces the selected Random Forest's held-out 2025 MAE to **17,479 passenger movements**, compared with approximately **451,552** for the original annual model. The **previous-month naive forecast remains slightly better at 16,481 MAE**, so v2.0 retains the baseline as the strongest tested one-step forecasting method rather than making an unsupported model-win claim.

The validation-selected Logistic Regression classifier achieves **0.781 balanced accuracy**, **0.739 F1**, and **0.886 ROC-AUC** on the untouched 2025 test set. Its confusion matrix is TN 688, FP 81, FN 196, TP 392.

## Open the website

On Windows, double-click `START_AIRCONNECT.bat`. Alternatively:

```powershell
python -m http.server 8080 --directory site
```

Then open <http://localhost:8080>. The packaged site also works by opening `site/index.html` directly and has no runtime network dependency.

## Install and reproduce

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install -r requirements-docs.txt
python src/build.py
python src/build_charts.py
python src/build_documents.py
python -m pytest -q
```

The editable slide deck is generated with the bundled Codex presentation runtime:

```powershell
$env:RUNTIME_NODE_MODULES='C:\Users\kasin\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\node_modules'
$env:CODEX_PRIMARY_RUNTIME_NODE_MODULES=$env:RUNTIME_NODE_MODULES
node src/build_presentation.mjs
```

Optional browser smoke testing requires Playwright and Chromium:

```powershell
python -m pip install playwright
python -m playwright install chromium
python tests/browser_smoke.py
```

## Dataset

- Source: [India Aviation Stats](https://github.com/mkubicek/india-aviation-stats), a cleaned DGCA-derived dataset, MIT licensed.
- Pinned upstream commit: `bce8fc78f2be1de88154c1d8e62d13ffc0d8e171`.
- Domestic monthly data: 13,599 records, 144 airports, April 2015 through partial 2026.
- Modelling window: April 2016 through December 2025; partial 2026 is excluded.
- Final test: January–December 2025, 1,357 eligible airport-month observations.
- Missing targets are never imputed. Exact-calendar lag gaps remain missing. Numeric feature imputation is fitted only inside each training fold.

Passenger movements mean arrivals plus departures, not unique travellers. Traffic-reporting airports are not the same as all operational airports, heliports, or water aerodromes.

## Methods

Regression compares Ridge, Decision Tree, Random Forest, and Histogram Gradient Boosting with previous-month, same-month-previous-year, and airport historical-mean baselines. Hyperparameters are selected on expanding 2022, 2023, and 2024 validation folds. Metrics are MAE, RMSE, R², WAPE, and median absolute error.

Classification predicts whether target-month domestic traffic is at least 10% above the same month one year earlier. Logistic Regression, CART, and Random Forest are compared with a majority-class dummy using the same chronological design.

K-Means evaluates k from 2 through 6 over six scaled 2025 airport features. A solution must contain at least five airports per cluster; when silhouette scores are within 0.02, the smaller k is preferred. PCA visualises the same feature space.

## Project structure

| Path | Purpose |
|---|---|
| `data/external/` | Unmodified pinned upstream CSVs and licence |
| `data/raw/` | Original v1 compact annual and coordinate inputs |
| `data/processed/analysis.json` | Canonical numerical source for site and documents |
| `src/pipeline.py` | Validation and exact-calendar feature construction |
| `src/modeling.py` | Chronological tuning, evaluation, K-Means, and PCA |
| `src/build.py` | Rebuild canonical analysis and browser data |
| `src/build_charts.py` | Generate figures from canonical results |
| `src/build_documents.py` | Generate the editable Word report |
| `src/build_presentation.mjs` | Generate and validate the editable PowerPoint deck |
| `site/` | Offline HTML, CSS, JavaScript website |
| `tests/` | Data, leakage, metric, model-output, and browser checks |
| `docs/` | Engineering plan, report, QA evidence, figures, DOCX, PPTX, PDFs |

## Limitations

- The forecast is one step ahead and assumes actual observations become available each month; it is not a recursive long-horizon forecast.
- COVID-19 creates substantial distribution shift in early validation history.
- Strong autocorrelation makes the previous-month baseline difficult to beat.
- Passenger counts alone do not measure capacity utilisation or explain route regulation.
- The 10% classification threshold is an analysis choice, not a government-defined class.

## Licence and attribution

The upstream cleaned dataset is MIT licensed and attributes its raw public source to India's Directorate General of Civil Aviation. See `data/external/india-aviation-stats/LICENSE` and `data/external/india-aviation-stats/README.md`. Project references and methodological details are in `docs/PROJECT_REPORT.md`.
