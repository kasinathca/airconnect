# AirConnect India

## Machine Learning-Based Analysis of Indian Airport Passenger Traffic and Connectivity

**Course:** MDI4001 Machine Learning for Data Science
**Institution:** Vellore Institute of Technology, Vellore  
**Team members:** [Enter names, register numbers, and university email addresses]
**Version:** 2.0.0
**Date:** 19 October 2026

## Abstract

AirConnect India studies airport passenger movements using a reproducible offline machine learning workflow. Version 2.0 replaces a small annual forecast with a one-step airport-month task constructed from 13,599 validated domestic records. Exact-calendar lags, shifted rolling statistics, seasonal terms, and airport identity are evaluated with expanding chronological validation and an untouched 2025 test period. The selected Random Forest achieves a 2025 MAE of 17,479 passenger movements, a substantial reduction from the original annual model's approximately 451,552, but the previous-month naive forecast remains stronger at 16,481 MAE. A supervised classifier predicts whether traffic is at least 10% above the same month one year earlier; validation selects Logistic Regression, which records 0.781 balanced accuracy and 0.886 ROC-AUC on 2025. K-Means selects four airport groups under a minimum-size and parsimony rule, with Silhouette Score 0.492. PCA represents 63.9% of standardised feature variance in two components. The principal conclusion is methodological: chronological evidence and strong baselines matter more than algorithm complexity.

**Keywords:** Indian aviation, passenger movements, time-series regression, classification, K-Means, PCA, chronological validation

## 1. Introduction

Indian aviation has expanded rapidly, but several quantities are often confused: operational facilities, airports reporting passenger traffic, airports recording international movements, and airports designated for international service. This project analyses recorded passenger movements without treating those categories as interchangeable. Passenger movements equal arrivals plus departures and therefore do not count unique travellers.

The original project provided a useful descriptive website and honest negative annual-forecast result, but its supervised dataset contained only about one hundred training observations. Version 2.0 uses monthly records to create a larger chronological panel while preserving the offline, small-project architecture.

## 2. Problem formulation and objectives

The primary regression question is: predict domestic passenger movements for airport A in month T using information available strictly before month T. This is a one-step-ahead evaluation. It assumes observed history becomes available each month and is not equivalent to recursive multi-month forecasting.

The classification question is: will target-month domestic traffic be at least 10% higher than the same month in the previous year? The threshold is an analytical choice for a compact syllabus-aligned problem, not an official government class.

Additional objectives are to identify interpretable airport groups, visualise multivariate structure with PCA, communicate uncertainty, and keep every numerical output reproducible.

## 3. Related work and data provenance

The source is Kubicek's *India Aviation Stats*, which cleans public DGCA workbooks into single-grain tables and documents difficult airport-identity decisions. AirConnect pins upstream commit `bce8fc78f2be1de88154c1d8e62d13ffc0d8e171` and preserves the MIT licence and SHA-256 hashes. Ministry of Civil Aviation figures are used only for broad expansion context, not as directly comparable traffic-reporting counts.

## 4. Dataset description

| Dataset | Grain | Rows | Airports | Coverage |
|---|---|---:|---:|---|
| Domestic monthly | Airport × month | 13,599 | 144 | April 2015 to partial 2026 |
| Airport yearly | Airport × year × category | 1,388 | 140 | 2015–2025 |
| International quarterly | Airport × quarter | 1,248 | 35 | 2015 to partial 2026 |

Core fields have no missing values, duplicate keys, or negative passenger counts. The pipeline verifies that passengers equal departures plus arrivals and reconciles complete domestic years between monthly and yearly tables. Partial 2026 is excluded from modelling. Eligible modelling rows run from April 2016 through December 2025.

## 5. System architecture

```text
Pinned CSV source and licence
            |
            v
validation and reconciliation
            |
            v
exact-calendar lag feature panel
      |             |             |
      v             v             v
 regression    classification  clustering/PCA
      \             |             /
       +------ canonical JSON ----+
                  |       |
                  v       v
              website   documents
```

Python performs validation, feature engineering, training, model selection, evaluation, chart generation, and document preparation. The website is static HTML, CSS, JavaScript, and SVG reading precomputed data.

## 6. Data preprocessing

Rows are ordered chronologically by airport. Each lag uses an exact date join rather than a simple previous-row shift. Missing months therefore remain missing. Targets are never imputed. For models requiring complete numeric inputs, median imputation is fitted only within the current training fold; airport identity uses one-hot encoding with unknown-category handling.

## 7. Feature engineering

The fifteen predictors are airport identity; lags 1, 2, 3, and 12; shifted rolling means over 3, 6, and 12 preceding months; counts of observed preceding months; one-month and lagged year-on-year growth; sine and cosine month terms; and a chronological index. Internally generated lag 13 supports the lagged year-on-year growth feature but is not directly supplied as a separate model feature.

For a target month t, the three-month rolling feature is:

`rolling3(t) = mean(y(t-1), y(t-2), y(t-3))`

Every term is before t. No target-year or target-month value enters the predictors.

## 8. Validation strategy

The final test period is January through December 2025 with 1,357 eligible airport-month observations. Expanding validation uses 2022, 2023, and 2024 as successive validation years; each fold trains only on earlier records. Hyperparameters are chosen from bounded grids using validation results. The final test is not used for selection.

This design exposes distribution shift, particularly the pandemic and recovery period. It also prevents the optimistic estimates that would result from randomly mixing future and past months.

## 9. Regression methodology

Candidates are Ridge Regression, Decision Tree Regressor, Random Forest Regressor, and Histogram Gradient Boosting. All predict `log(1 + traffic)` and are inverted to original passenger units. Baselines are previous month, same month previous year, and airport historical mean.

The metrics are:

- `MAE = mean(|y - y_hat|)`
- `RMSE = sqrt(mean((y - y_hat)^2))`
- `R² = 1 - sum((y - y_hat)^2) / sum((y - mean(y))^2)`
- `WAPE = sum(|y - y_hat|) / sum(|y|)` when the denominator is nonzero
- Median absolute error

Random Forest is selected among trained models by validation MAE with 180 trees, depth 16, minimum leaf size 5, and all transformed features considered per split.

## 10. Regression results

| Method | Type | Validation MAE | Test MAE | Test RMSE | Test R² | Test WAPE |
|---|---|---:|---:|---:|---:|---:|
| Ridge Regression | Trained | 135,038 | 162,333 | 1,721,109 | -6.1304 | 66.06% |
| Decision Tree | Trained | 28,749 | 21,434 | 61,018 | 0.9910 | 8.72% |
| Random Forest | Trained | 24,769 | 17,479 | 50,430 | 0.9939 | 7.11% |
| Histogram Gradient Boosting | Trained | 39,217 | 20,977 | 67,784 | 0.9889 | 8.54% |
| Previous month naive | Baseline | 17,880 | 16,481 | 46,579 | 0.9948 | 6.71% |
| Seasonal naive | Baseline | 49,576 | 22,668 | 55,234 | 0.9927 | 9.22% |
| Airport historical mean | Baseline | 58,337 | 62,708 | 172,392 | 0.9285 | 25.52% |

The Random Forest improves dramatically over the original annual model but does not beat the previous-month baseline. The short horizon and strong traffic persistence explain why lag 1 dominates permutation importance. This is a defensible negative result, not a failure to report.

## 11. Regression error analysis

| Prior-year traffic segment | Random Forest MAE | Previous-month MAE | Test rows |
|---|---:|---:|---:|
| Lower | 1,431 | 1,314 | 436 |
| Middle | 6,616 | 6,438 | 446 |
| Higher | 42,409 | 39,834 | 475 |

Large airports dominate aggregate passenger error even when proportional error is moderate. Median absolute error for Random Forest is 3,265, which is far below its MAE because a small number of high-volume observations carry large absolute residuals.

## 12. Classification methodology

Class 1 is assigned only when the actual target-month value is at least 1.10 times the actual same month one year earlier and that denominator is positive. Predictors remain pre-target. Logistic Regression, Decision Tree Classifier, and Random Forest Classifier are compared with a majority-class dummy. Selection maximises mean validation balanced accuracy at decision threshold 0.50.

The positive class is at least 10% growth. Precision measures the share of predicted growth cases that truly meet the threshold; recall measures the share of true growth cases detected; F1 balances both. True negatives and true positives are correct predictions, while false positives and false negatives are the corresponding error types.

## 13. Classification results

| Model | Accuracy | Balanced accuracy | Precision | Recall | F1 | ROC-AUC | Average precision |
|---|---:|---:|---:|---:|---:|---:|---:|
| Logistic Regression | 0.7959 | 0.7807 | 0.8288 | 0.6667 | 0.7389 | 0.8862 | 0.8445 |
| Decision Tree | 0.8040 | 0.7920 | 0.8194 | 0.7024 | 0.7564 | 0.8780 | 0.8190 |
| Random Forest | 0.8224 | 0.8169 | 0.8071 | 0.7755 | 0.7910 | 0.9079 | 0.8834 |
| Majority dummy | 0.4333 | 0.5000 | 0.4333 | 1.0000 | 0.6046 | — | — |

Validation selected Logistic Regression before the test was opened. Its test confusion counts are TN 688, FP 81, FN 196, and TP 392. Random Forest scores higher on the final test but is reported as a comparison rather than retroactively selected.

## 14. K-Means clustering

Six 2025 airport features are median-imputed where required and standardised: log domestic traffic, log international traffic, domestic growth, monthly seasonality coefficient of variation, international share, and active months. K values from 2 through 6 are evaluated.

| k | Inertia | Silhouette | Minimum cluster size |
|---:|---:|---:|---:|
| 2 | 521.42 | 0.4284 | 31 |
| 3 | 367.19 | 0.4640 | 26 |
| 4 | 274.58 | 0.4916 | 7 |
| 5 | 215.88 | 0.5021 | 4 |
| 6 | 173.47 | 0.4852 | 4 |

Although k = 5 has the highest silhouette, its smallest cluster contains only four airports and fails the declared viability rule. Therefore k = 4 is selected.

| Cluster | Airports | Median domestic | Median international | Median annual growth | Median seasonality CV |
|---|---:|---:|---:|---:|---:|
| Small airports | 21 | 15,702 | 0 | -48.60% | 0.6550 |
| Regional airports | 7 | 40,966 | 0 | 375.08% | 0.5998 |
| Large airports | 70 | 295,450 | 0 | 7.44% | 0.1450 |
| Major gateways | 31 | 4,196,156 | 555,408 | 5.94% | 0.0804 |

Names are post-fit summaries based on medians, not normative labels. The high-growth seven-airport group likely captures rapid ramp-up and should not be interpreted as proof of capacity utilisation.

## 15. Principal component analysis

PCA is fitted to the same standardised six-feature matrix. PC1 explains 44.85% and PC2 explains 19.02%, for cumulative explained variance of 63.87%. PC1 loads positively on domestic scale, international scale, and international share, and negatively on seasonality. PC2 loads most positively on international share and seasonality and negatively on active months. PCA visualises a compressed feature space; it does not create the K-Means labels.

## 16. Hyperparameter tuning

The search is bounded and reproducible. Ridge considers three regularisation values. Decision trees consider four depth/leaf combinations. Random Forest considers four configurations for depth, leaf size, and feature sampling with 180 estimators. Histogram Gradient Boosting considers four learning-rate, leaf-node, leaf-size, and L2 configurations. Classification applies similarly small grids. Seed 37 is fixed where supported.

## 17. Model evaluation and selection

Selection and final reporting are separated. The test set is used once after validation choice. The project distinguishes a selected ML model from the strongest overall forecasting method: Random Forest is the trained-model choice, while the previous-month naive method is the overall winner on 2025 MAE.

## 18. Visual analysis

The generated figures include annual traffic, regression model comparison, actual-versus-predicted values, residual scatter and histogram, traffic-size errors, permutation importance, confusion matrix, ROC and precision-recall curves, classifier metrics, K-Means inertia and silhouette, cluster sizes, PCA projection, and explained variance. Website SVG marks provide focusable tooltips, and tables provide numerical alternatives.

## 19. Website implementation

The website retains Overview, Airport Explorer, Machine Learning, and Methodology. Machine Learning uses three sub-tabs instead of expanding the main navigation. Filters support year, cluster, airport search, and CSV export. Custom tooltips work on hover, keyboard focus, and touch and are dismissed with Escape. The interface uses local assets and operates offline.

## 20. Reproducibility and software engineering

Responsibilities are separated across source validation, feature construction, modelling, artifact export, charts, documents, and browser presentation. `analysis.json` is the numerical source of truth. Tests independently recalculate metrics, verify confusion totals, inspect PCA dimensions, and exercise the site. GitHub Actions runs the offline test suite.

## 21. Ablation note

A formal feature ablation study was not performed. Permutation importance was calculated on the held-out test predictions only for explanation, not for feature selection. Therefore the project does not claim causal feature contribution or an ablation result.

## 22. Findings and discussion

Monthly granularity solves much of the original sample-size problem and materially improves trained-model error. It does not guarantee that a complex model will beat a correctly chosen baseline. The selected Random Forest relies overwhelmingly on the immediately preceding month, which is consistent with stable airport traffic series. Classification is more successful relative to its dummy benchmark and provides a legitimate setting for confusion-matrix analysis.

The four clusters reveal scale, international participation, seasonality, and growth differences, while PCA shows that two components retain roughly two-thirds of standardised variance. Neither method establishes causal explanations.

## 23. Limitations

- The one-step evaluation uses actual lagged observations and does not test recursive forecasts.
- Pandemic disruption affects the historical folds.
- Airport openings, closures, and coding changes may cause structural breaks.
- Missing rows are not zeros; eligibility can favour airports with more continuous reporting.
- Absolute error is dominated by large airports, while proportional metrics can overemphasise small denominators.
- The classifier threshold is analytically chosen.
- Passenger data alone cannot establish capacity utilisation, service accessibility, or regulation.

## 24. Conclusion

AirConnect India v2.0 provides a technically sound and presentation-ready academic case study without overstating its evidence. Monthly data, exact-calendar features, chronological validation, real classification, defensible clustering, and a canonical result artifact substantially improve the original implementation. The strongest one-step forecast remains a simple previous-month baseline. Reporting that result is central to the project's methodological value.

## References

1. Kubicek, M. (2026). *India Aviation Stats: a cleaned DGCA passenger-traffic dataset*. GitHub. https://github.com/mkubicek/india-aviation-stats
2. Directorate General of Civil Aviation, Government of India. Public aviation traffic workbooks, as transformed and documented by the source repository.
3. Ministry of Civil Aviation, Government of India. Operational airport listings and aviation expansion releases. https://www.civilaviation.gov.in/
4. Pedregosa, F. et al. (2011). Scikit-learn: Machine Learning in Python. *Journal of Machine Learning Research*, 12, 2825–2830.
5. Rousseeuw, P. J. (1987). Silhouettes: a graphical aid to the interpretation and validation of cluster analysis. *Journal of Computational and Applied Mathematics*, 20, 53–65.
