# Presentation guide — AirConnect India

**Presentation duration:** 7–9 minutes. Replace the member-name placeholders before presenting.

| Slide | What to explain |
|---|---|
| 1. Title | Indian airport growth versus observed passenger activity; classic ML models |
| 2. Motivation | 74 operational airports in 2014 versus 165 in July 2026; those totals are not identical to traffic-reporting airports |
| 3. Objective | Data analysis, clustering, regression and an offline interactive website |
| 4. Dataset | DGCA-derived passenger arrivals + departures; 2016–2025 national series and 2022–2025 airport-level sample; 614 source rows |
| 5. Workflow | Source → checks → airport/year pivot → scaling/lag features → model → results website |
| 6. Clustering | Log transform, standardise, k = 3; n = 129; Silhouette = 0.6235; explain three groups |
| 7. Random Forest | Lag-one and lag-two traffic; train on 2024, test on 2025; no future-data leakage |
| 8. Results | Forest MAE 451,552 versus baseline MAE 182,476: baseline wins; explain honest negative finding |
| 9. Live demo | Filter 2025 map for COK, compare records and examine model scores and source notes |
| 10. Conclusion | Traffic growth, concentration, differentiation of counts; model limitations, future enhancements |

## Likely faculty questions

**Why K-Means?** We do not have ground-truth labels for airports; clustering can discover groups based on numerical annual traffic profiles.

**Why standardise?** Domestic and international traffic have different distributions, and K-Means uses Euclidean distances. `log1p` reduces scale skew.

**How did you choose k = 3?** It is a small, interpretable demonstrator choice. The Silhouette Score evaluates separation. We do not claim it is globally optimal without a multi-k comparison.

**What does an international value of zero mean?** No corresponding international category row was present in the analysed input; it does not imply legal flight restrictions.

**Why did Random Forest lose?** The previous-year persistence baseline is very strong for relatively stable airport traffic. Training annual samples are limited, and tree models can struggle to extrapolate beyond observed scales.

**What is R²?** A measure of how much of the variation in the held-out targets is explained relative to predicting the mean; do not treat it as classification accuracy.

**Does low traffic mean airport is not used properly?** No. Capacity utilisation needs runway/terminal/seat capacity and load information, which are not present in this dataset.

**Can it run offline?** Yes. `site/index.html` reads bundled JS data. The original ML training can also be reproduced locally with Python.
