# AIRCONNECT INDIA
## Machine Learning-Based Analysis of Indian Airport Passenger Traffic and Connectivity

**Course:** MDI4001 — Machine Learning for Data Science (Laboratory)  
**Institution:** Vellore Institute of Technology, Vellore  
**Team members:** [Enter the participating student names, register numbers and university email addresses]  
**Academic year:** 2026–2027

## Abstract

India's aviation infrastructure has expanded rapidly, but airport openings and airport utilisation cannot be evaluated solely from headline totals. This project analyses the growth in passenger traffic in Indian airports and uses two classical machine learning algorithms to identify airport traffic patterns and evaluate annual passenger-volume forecasting. A curated Directorate General of Civil Aviation (DGCA)-derived dataset supplies 2016–2025 national domestic and international passenger movement totals, with 2022–2025 airport-level annual records used for machine learning. Data are processed into airport–year observations, and a K-Means model classifies 129 airports by their 2025 annual domestic and international passenger movements. A Random Forest regressor is evaluated on a chronological 2025 test year against a prior-year baseline. The three-cluster model achieves a Silhouette Score of **0.6235**, while the baseline outperforms Random Forest on the 2025 test set. Results are presented in an offline HTML research website featuring historical charts, a simplified India airport map, search, filters and downloadable data. The study distinguishes observed traffic from capacity utilisation and administrative international-airport classifications.

**Keywords:** India aviation; airport passenger movements; K-Means; Random Forest; time-aware validation; regression; passenger traffic; data visualisation.

## 1. Introduction

Airport infrastructure provides transport connectivity and supports economic activity, but counting operational airports does not directly measure the volume of passenger services. India's Ministry of Civil Aviation reports an increase from **74 operational facilities in 2014** to **165 as of 7 July 2026**. These counts include facilities whose reporting definitions differ from the airports contributing passenger movement records. This project examines airport-level traffic instead of inferring utilisation from infrastructure counts.

### 1.1 Problem statement

Investigate changes in domestic and international passenger movement totals; segment airports with similar annual traffic; test the accuracy of a simple ML prediction model using held-out calendar-year records.

### 1.2 Objectives

1. Prepare, audit and visualise DGCA-derived traffic data.
2. Contrast national traffic patterns with reported operational-airport growth.
3. Apply K-Means clustering to traffic variables and interpret the resulting airport groups.
4. Train Random Forest regression using lagged annual passenger movements.
5. Benchmark the regression against the preceding year's traffic and report MAE, RMSE and R².
6. Present interactive results through a local HTML/CSS/JavaScript application.

## 2. Related work and background

The Ministry of Civil Aviation maintains operational aviation facility counts and descriptions of the regional connectivity programme (RCS-UDAN). DGCA statistical tables report observed airport and airline passenger traffic. The independently maintained India Aviation Stats repository (Kubicek, 2026) normalises those DGCA workbooks into consistent CSV tables and documents decisions needed to reconcile airport codes and spelling variants. The project's classification of airports according to their passenger movements is therefore based on observed transport activity rather than airport designation. K-Means provides transparent exploratory segmentation, while Random Forest represents a syllabus-aligned nonlinear regression approach suitable for numerical features.

The accessibility map published at Visualized.in motivated the research question but is not reproduced by this project, because historical weekly service and geospatial coverage data are different from the annual passenger dataset.

## 3. Dataset and preprocessing

| Input | Coverage | Purpose |
|---|---|---|
| National annual passenger totals | 2016–2025 | Long-run movement comparison |
| Airport yearly domestic and international records | 2022–2025; 614 category rows | Airport-level analyses and ML |
| Airport coordinate records | 93 of 129 domestic reporting airports matched for 2025 | Geographic view |
| Government airport counts | 2014 and 7 July 2026 | Contextual infrastructure comparison |

**Data unit:** Number of passenger movements, where arrivals and departures both contribute. The counts must not be interpreted as unique travellers. The 2022–2025 input contains **614 airport–year–category rows**. These are pivoted into **491 airport–year observations**. A missing international category is filled with zero for model features but is interpreted conservatively as no corresponding annual international record in the input, not evidence of a legal prohibition.

**Preparation workflow:**

1. Validate the fields `year`, `airport`, `category` and `passengers`.
2. Check for nonnegative passenger values and duplicate (`year`, `airport`, `category`) keys.
3. Verify category sums exactly against the separately derived annual source totals.
4. Pivot domestic and international counts into numerical airport–year columns.
5. For K-Means, apply `log(1 + passengers)` separately to both traffic types, followed by standard scaling.
6. For regression, construct preceding-year and two-years-prior domestic passenger predictors only when all requisite years are available.

### 3.1 National passenger volume

| Year | Domestic movements | International movements |
|---|---:|---:|
| 2016 | 198,946,866 | 53,673,140 |
| 2019 | 287,472,512 | 63,661,178 |
| 2020 | 125,704,022 | 17,092,876 |
| 2022 | 246,484,028 | 46,920,910 |
| 2023 | 304,080,934 | 63,881,888 |
| 2024 | 322,650,506 | 72,210,403 |
| 2025 | 333,873,006 | 77,979,936 |

Domestic movement volume increased by **67.8% from 2016 to 2025**. The 2020 fall is consistent with the pandemic period, and it demonstrates why this time series should not be represented as uninterrupted policy-driven growth.

## 4. Methods

### 4.1 K-Means airport segmentation

**Input observations:** 129 airports with a 2025 domestic passenger record.  
**Feature vector:** `X_i = [log(1 + domestic_i), log(1 + international_i)]`.  
**Scaling:** StandardScaler applied to the 2025 feature matrix.  
**Algorithm:** KMeans(`n_clusters=3`, `random_state=37`, `n_init=20`).  
**Evaluation:** Silhouette Score; group frequencies and median passenger volumes.  
**Post-fit labelling:** Relabel groups by ascending median total movements as Lower traffic, Intermediate traffic and Major gateways. These names are descriptive interpretations, not training labels.

### 4.2 Random Forest domestic passenger regression

**Prediction task:** Predict annual domestic passenger movements for a given airport, one calendar year ahead.  
**Inputs:** `lag1 = traffic(year − 1)` and `lag2 = traffic(year − 2)`, transformed with `log1p`.  
**Model target:** `log1p(traffic(year))` for numeric stability.  
**Training:** Airports with complete 2022–2024 data, predicting 2024.  
**Testing:** Airports with complete 2023–2025 data, predicting 2025.  
**Hyperparameters:** 120 estimators, max depth 9, minimum leaf 2, random seed 37.  
**Inverse transform:** `expm1` returns forecasts in passenger movement units.  
**Baseline:** The preceding year's domestic passenger count without fitted parameters.

**Metric definitions:**

- Mean Absolute Error: `MAE = mean(|actual − predicted|)`.
- Root Mean Squared Error: `RMSE = sqrt(mean((actual − predicted)^2))`.
- Coefficient of determination: `R² = 1 − sum((actual − predicted)^2) / sum((actual − actual_mean)^2)`.

A chronological split is necessary because randomly mixing airport-year rows would overstate the validity of a historical forecasting exercise.

## 5. Experimental results

### 5.1 Clustering

**Silhouette Score = 0.6235**, with **k = 3**, **n = 129**.

| Interpreted group | Airports | Median domestic movements | Median international movements | Examples |
|---|---:|---:|---:|---|
| Lower traffic | 36 | 13,795 | 0 | CDP, JGB, HJR |
| Intermediate traffic | 62 | 408,804 | 0 | GOI, PAT, SXR |
| Major gateways | 31 | 4,196,156 | 555,408 | DEL, BOM, BLR |

The third cluster captures larger airports with recorded international traffic. The smaller groups exhibit far lower median movement volumes and typically no international row. The Silhouette Score shows reasonably clear separation in the chosen transformed two-feature space; it is not a classification accuracy measure.

### 5.2 Regression versus baseline

| Measure | Random Forest | Prior-year baseline | Better |
|---|---:|---:|---|
| Training airport observations | 106 | No training | — |
| Test airport observations | 116 | 116 | — |
| MAE | 451,551.93 | 182,476.34 | Baseline |
| RMSE | 2,044,383.36 | 354,819.58 | Baseline |
| R² | 0.9282 | 0.9978 | Baseline |

The Random Forest produced plausible overall ranking but made substantially larger errors than the persistence baseline. Limited annual training observations and the difficulty of extrapolating unusually large hub volumes are possible reasons. Therefore, the study does **not** claim a practical forecasting improvement. The numerical result is still useful for demonstrating the importance of baselines, metric choice and chronological holdouts.

### 5.3 Feature contribution

Random Forest training feature importances were approximately **0.745** for the preceding year's traffic and **0.255** for two-years-prior traffic. These are fitted model importances, not causal explanations. No claim of a capacity-utilisation threshold is drawn from the cluster labels.

## 6. Software design and validation

The software follows a simple offline data pipeline: preserved source CSV → validation → feature construction → fitted scikit-learn models → generated static JSON → HTML/CSS/JavaScript visualisation. The web app uses semantic HTML, keyboard-accessible navigation and map markers, native hover tooltips, local vector graphics, responsive layout and downloadable CSV export. No registration, map tile service, cloud account or server is necessary to demonstrate the project.

**Verification performed:**

- Five automated Python tests passed, checking input counts, duplicate absence, year totals, metric consistency, static assets and reproducible regeneration.
- Browser interaction smoke checks at 1440px desktop and 390px mobile widths passed with no JavaScript page errors and no page-level horizontal overflow.
- Airport search, year filter, group filtering, table pagination and clickable map marker interactions were exercised.
- Documentation states the feature coverage and source differences explicitly.

## 7. Conclusions, limitations and extensions

**Conclusions:** (i) recorded passenger movements increased during the 2016–2025 period, despite the COVID-era interruption; (ii) airports exhibit distinct domestic/international traffic profiles that K-Means can segment; (iii) a naive persistence predictor can outperform a substantially more complex fitted regressor on near-term annual passenger totals; and (iv) airport-growth counts and airport traffic statistics are related but not interchangeable.

**Limitations:** National facility counts are not an annual construction series. The geographic map covers only airports with matched coordinates. International passenger volumes cannot identify bilateral point-of-call permissions or airline route approvals. Neither the source data nor the models measure terminal capacity, runway utilisation, available seats, pilot supply, or population within 100 km of service. Reported airport-year data begins in 2022 for the distributed airport-level subset, limiting the supervised training sample.

**Potential future extensions:** Include reliable month-level histories and airline seat-capacity data, rerun comparisons with more training years, use suitable temporal cross-validation, and add accurate time-indexed active route coverage maps. These additions are outside the current laboratory scope.

## References

[1] M. Kubicek, *India Aviation Stats: a cleaned DGCA passenger-traffic dataset*, 2026. https://github.com/mkubicek/india-aviation-stats

[2] Ministry of Civil Aviation, Government of India, *Airports*, operational airport count through 7 July 2026. https://www.civilaviation.gov.in/index.php/node/4628

[3] Ministry of Civil Aviation, Government of India, *India had 74 operational airports in 2014*, June 2026. https://www.civilaviation.gov.in/node/7425

[4] B. Himpfen, *Airports Dataset*, GitHub, MIT. https://github.com/brandonhimpfen/airports

[5] Natural Earth, *Free vector and raster map data*, public domain. https://www.naturalearthdata.com/

[6] *Visualized.in*, *India's airport accessibility*, background research reference. https://visualized.in/airports
