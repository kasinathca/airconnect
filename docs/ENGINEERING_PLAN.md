# Software Engineering Plan — AirConnect India

**Document control:** v1.0 | 19 October 2026 | MDI4001 course project

## 1. Purpose and scope

A locally executable, offline static website presents Indian passenger airport traffic and ML findings for a small academic laboratory evaluation. Training uses Python; the web app only visualises precomputed data, improving reproducibility and reducing operational failure modes.

### Functional requirements

| ID | Requirement | Acceptance |
|---|---|---|
| FR-01 | Show source-qualified national aviation indicators | Counts, periods and definitions displayed |
| FR-02 | Visualise national passenger traffic 2016–2025 | Historical chart with hover titles |
| FR-03 | Explore airport-level annual records 2022–2025 | Year switch, search and table ranking |
| FR-04 | Show a geographic view | Local map, hover descriptions, accessible marker interaction |
| FR-05 | Explain K-Means output | Cluster count, group sizes, centroids/medians, Silhouette Score |
| FR-06 | Evaluate supervised model | Test split, MAE/RMSE/R², baseline comparison, actual/predicted plot |
| FR-07 | Export selected airport records | Download filtered CSV |
| FR-08 | Explain provenance and limitations | Accessible methodology page and bundled research notes |

### Nonfunctional requirements

| ID | Requirement | Design decision |
|---|---|---|
| NFR-01 | Offline-first | No network requests, CDN, analytics or login |
| NFR-02 | Short setup | Double-click index.html / batch launcher |
| NFR-03 | Reproducibility | Fixed seed 37; bundled numeric records; generated JSON |
| NFR-04 | Accessibility | Semantic HTML, labels, focus states, chart descriptions, keyboard marker activation, reduced motion |
| NFR-05 | Responsive design | Desktop and narrow mobile viewport layout |
| NFR-06 | Academic appearance | Neutral palette, Segoe UI and Cambria, restrained typography, compact interaction |
| NFR-07 | Data honesty | Definitions stated; no inferred causality or made-up airport openings |

## 2. Architecture

```text
DGCA-derived annual CSV   Government series   Airport coordinates
           \                 |                 /
                    input validation
                           |
                  airport-year features
                           |
             +-------------+--------------+
             |                            |
       K-Means 2025               RF year-ahead regression
        k=3 / scaling              2024 train / 2025 test
             |                            |
             +-------------+--------------+
                           |
            data/processed/analysis.json
                           |
                   site/assets/data.js
                           |
                 Offline HTML / CSS / JS
```

The static viewer has no privileged operations and stores no user data. Every screen can be viewed without Python, because the models have already been trained. To reproduce, run `python src/build.py`.

## 3. Modules and responsibilities

- `src/seed_data.py`: source-preserving base36 encoding and CSV unpacking; provides source-defined annual national series.
- `src/build.py`: input validation, pivoting, feature construction, unsupervised clustering, chronological regression evaluation, static JSON generation.
- `site/index.html`: semantic structure and page content.
- `site/assets/style.css`: responsive Microsoft Fluent-inspired visual language.
- `site/assets/app.js`: user-facing filters, charts, map interactions, data export and explanations.
- `site/assets/data.js`: generated data artifact; do not modify manually.

## 4. Data governance

- Reuse the exact airport passenger-movement definitions supplied by the clean DGCA-derived source.
- Retain the full annual four-year source subset and separately calculated earlier national aggregates, without inventing missing airport rows.
- Interpret missing international records as *not reported in the input table*, represented as zero for the charting feature, not as proof of legal restrictions.
- Use an explicit chronological train/test split and avoid target-year features in the forecast.
- Review and cite third-party licence terms in the README.

## 5. Evaluation gates

1. Every input category count matches the archived annual source totals exactly.
2. One and only one record per year–airport–category.
3. Cluster membership totals equal the number of 2025 airports used for clustering.
4. Regression train and test years are disjoint; no target-year feature leakage.
5. Predicted values and metric calculations are finite and numerically consistent.
6. Site opens without a backend; tab navigation, search, year switching, CSV export and tooltip/title elements are functional.
7. Desktop and mobile renderings have no horizontal document overflow.

## 6. Known limitations and deferred work

Excluded: hexagonal network-distance map, yearly lists of airport opening dates, geographic population accessibility, slot utilisation, bilateral aviation treaty simulation, forecasting beyond the held-out historical year, interactive cloud database and live API calls.

These exclusions are deliberate scope controls, not incomplete code paths.
