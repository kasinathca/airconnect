"""Chronological model selection and unsupervised analysis for AirConnect India."""
from __future__ import annotations

from itertools import product
from typing import Any, Callable

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.compose import ColumnTransformer
from sklearn.decomposition import PCA
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestClassifier, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import (
    accuracy_score, average_precision_score, balanced_accuracy_score, confusion_matrix,
    f1_score, mean_absolute_error, mean_squared_error, median_absolute_error,
    precision_recall_curve, precision_score, r2_score, recall_score, roc_auc_score,
    roc_curve, silhouette_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor


SEED = 37
NUMERIC_FEATURES = [
    "lag1", "lag2", "lag3", "lag12", "rolling_mean_3", "rolling_mean_6",
    "rolling_mean_12", "observed_prior_6", "observed_prior_12", "growth_1m",
    "growth_yoy_lag", "month_sin", "month_cos", "time_index",
]
CATEGORICAL_FEATURES = ["airport"]
ALL_FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES
CV_YEARS = [2022, 2023, 2024]
TEST_YEAR = 2025


def _preprocessor() -> ColumnTransformer:
    numeric = Pipeline([("imputer", SimpleImputer(strategy="median", add_indicator=True)), ("scale", StandardScaler())])
    categorical = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    return ColumnTransformer([("numeric", numeric, NUMERIC_FEATURES), ("airport", categorical, CATEGORICAL_FEATURES)], sparse_threshold=0)


def _pipe(estimator: Any) -> Pipeline:
    return Pipeline([("preprocess", _preprocessor()), ("model", estimator)])


def regression_metrics(actual: np.ndarray, predicted: np.ndarray) -> dict[str, float | None]:
    denom = float(np.abs(actual).sum())
    return {
        "mae": round(float(mean_absolute_error(actual, predicted)), 2),
        "rmse": round(float(np.sqrt(mean_squared_error(actual, predicted))), 2),
        "r2": round(float(r2_score(actual, predicted)), 4),
        "wape": round(float(np.abs(actual - predicted).sum() / denom), 6) if denom else None,
        "median_ae": round(float(median_absolute_error(actual, predicted)), 2),
    }


def _regression_candidates() -> dict[str, list[tuple[dict[str, Any], Callable[[], Any]]]]:
    return {
        "Ridge regression": [({"alpha": a}, lambda a=a: Ridge(alpha=a)) for a in [1.0, 10.0, 50.0]],
        "Decision Tree": [
            ({"max_depth": d, "min_samples_leaf": l}, lambda d=d, l=l: DecisionTreeRegressor(max_depth=d, min_samples_leaf=l, random_state=SEED))
            for d, l in [(6, 10), (10, 10), (10, 25), (None, 25)]
        ],
        "Random Forest": [
            ({"n_estimators": 180, "max_depth": d, "min_samples_leaf": l, "max_features": f},
             lambda d=d, l=l, f=f: RandomForestRegressor(n_estimators=180, max_depth=d, min_samples_leaf=l, max_features=f, random_state=SEED, n_jobs=1))
            for d, l, f in [(12, 2, 0.7), (None, 2, 0.7), (16, 5, 1.0), (None, 5, 1.0)]
        ],
        "Histogram Gradient Boosting": [
            ({"learning_rate": r, "max_leaf_nodes": n, "min_samples_leaf": m, "l2_regularization": l2, "max_iter": 220},
             lambda r=r, n=n, m=m, l2=l2: HistGradientBoostingRegressor(learning_rate=r, max_leaf_nodes=n, min_samples_leaf=m, l2_regularization=l2, max_iter=220, random_state=SEED))
            for r, n, m, l2 in [(0.05, 15, 20, 0.1), (0.05, 31, 30, 1.0), (0.10, 15, 30, 1.0), (0.10, 31, 40, 2.0)]
        ],
    }


def _fit_predict_log(factory: Callable[[], Any], train: pd.DataFrame, test: pd.DataFrame) -> tuple[Pipeline, np.ndarray]:
    model = _pipe(factory())
    model.fit(train[ALL_FEATURES], np.log1p(train.target.to_numpy(float)))
    return model, np.clip(np.expm1(model.predict(test[ALL_FEATURES])), 0, None)


def run_regression(panel: pd.DataFrame) -> dict[str, Any]:
    candidates = _regression_candidates()
    chosen, validation_rows = {}, []
    for name, configurations in candidates.items():
        scored = []
        for params, factory in configurations:
            errors = []
            for year in CV_YEARS:
                train, valid = panel[panel.year < year], panel[panel.year == year]
                _, pred = _fit_predict_log(factory, train, valid)
                errors.append(mean_absolute_error(valid.target, pred))
            scored.append((float(np.mean(errors)), params, factory))
        mean_mae, params, factory = min(scored, key=lambda item: item[0])
        chosen[name] = (params, factory, mean_mae)
        for year in CV_YEARS:
            train, valid = panel[panel.year < year], panel[panel.year == year]
            _, pred = _fit_predict_log(factory, train, valid)
            validation_rows.append({"model": name, "fold_year": year, "n": len(valid), **regression_metrics(valid.target.to_numpy(float), pred)})

    for baseline_name, column in [("Previous month naive", "lag1"), ("Seasonal naive", "lag12")]:
        for year in CV_YEARS:
            valid = panel[panel.year == year]
            validation_rows.append({"model": baseline_name, "fold_year": year, "n": len(valid), **regression_metrics(valid.target.to_numpy(float), valid[column].to_numpy(float))})
    for year in CV_YEARS:
        train, valid = panel[panel.year < year], panel[panel.year == year]
        pred = valid.airport.map(train.groupby("airport").target.mean()).fillna(train.target.median()).to_numpy(float)
        validation_rows.append({"model": "Airport historical mean", "fold_year": year, "n": len(valid), **regression_metrics(valid.target.to_numpy(float), pred)})

    validation = pd.DataFrame(validation_rows)
    validation_summary = [{"model": name, "folds": len(group), "observations": int(group.n.sum()),
                           **{key: round(float(group[key].mean()), 4) for key in ["mae", "rmse", "r2", "wape", "median_ae"]}}
                          for name, group in validation.groupby("model", sort=False)]
    train, test = panel[panel.year < TEST_YEAR].copy(), panel[panel.year == TEST_YEAR].copy()
    test_results, fitted, predictions = [], {}, {}
    for name, (params, factory, _) in chosen.items():
        model, pred = _fit_predict_log(factory, train, test)
        fitted[name], predictions[name] = model, pred
        test_results.append({"model": name, "type": "trained", "hyperparameters": params, **regression_metrics(test.target.to_numpy(float), pred)})
    baseline_predictions = {
        "Previous month naive": test.lag1.to_numpy(float), "Seasonal naive": test.lag12.to_numpy(float),
        "Airport historical mean": test.airport.map(train.groupby("airport").target.mean()).fillna(train.target.median()).to_numpy(float),
    }
    for name, pred in baseline_predictions.items():
        predictions[name] = pred
        test_results.append({"model": name, "type": "baseline", "hyperparameters": {}, **regression_metrics(test.target.to_numpy(float), pred)})
    trained_validation = [row for row in validation_summary if row["model"] in candidates]
    selected_name = min(trained_validation, key=lambda row: row["mae"])["model"]
    selected_pred = predictions[selected_name]
    best_baseline = min((row for row in test_results if row["type"] == "baseline"), key=lambda row: row["mae"])
    selected_test = next(row for row in test_results if row["model"] == selected_name)

    q1, q2 = train.lag12.quantile([0.33, 0.66]).tolist()
    segment = pd.cut(test.lag12, [-np.inf, q1, q2, np.inf], labels=["Lower", "Middle", "Higher"])
    segments = []
    for name in [selected_name, best_baseline["model"]]:
        for label in ["Lower", "Middle", "Higher"]:
            mask = (segment == label).to_numpy()
            segments.append({"method": name, "segment": label, "n": int(mask.sum()), **regression_metrics(test.loc[mask, "target"].to_numpy(float), predictions[name][mask])})

    rng = np.random.default_rng(SEED)
    base_mae = mean_absolute_error(test.target, selected_pred)
    importance = []
    for feature in ALL_FEATURES:
        permuted = test[ALL_FEATURES].copy()
        permuted[feature] = rng.permutation(permuted[feature].to_numpy())
        shuffled = np.clip(np.expm1(fitted[selected_name].predict(permuted)), 0, None)
        importance.append({"feature": feature, "mae_increase": round(float(mean_absolute_error(test.target, shuffled) - base_mae), 2)})
    importance.sort(key=lambda row: row["mae_increase"], reverse=True)
    records = [{"airport": row.airport, "date": row.date.strftime("%Y-%m"), "actual": int(row.target),
                "selected_prediction": round(float(selected_pred[idx]), 2), "seasonal_naive": round(float(row.lag12), 2),
                "residual": round(float(row.target - selected_pred[idx]), 2)}
               for idx, row in test.reset_index(drop=True).iterrows()]
    return {
        "task": "One-step-ahead domestic airport-month passenger movement prediction",
        "training_period": [str(panel.date.min().date()), "2024-12-01"], "validation_years": CV_YEARS,
        "test_period": ["2025-01-01", "2025-12-01"], "train_n": len(train), "test_n": len(test),
        "feature_count": len(ALL_FEATURES), "features": ALL_FEATURES, "validation": validation_summary,
        "validation_folds": validation_rows, "test": test_results, "selected_model": selected_name,
        "selected_hyperparameters": chosen[selected_name][0], "best_baseline": best_baseline["model"],
        "beat_best_test_baseline": bool(selected_test["mae"] < best_baseline["mae"]),
        "segments": segments, "feature_importance": importance, "predictions": records,
    }


def classification_metrics(actual: np.ndarray, predicted: np.ndarray, probability: np.ndarray | None) -> dict[str, Any]:
    tn, fp, fn, tp = confusion_matrix(actual, predicted, labels=[0, 1]).ravel()
    result = {"accuracy": round(float(accuracy_score(actual, predicted)), 6),
              "balanced_accuracy": round(float(balanced_accuracy_score(actual, predicted)), 6),
              "precision": round(float(precision_score(actual, predicted, zero_division=0)), 6),
              "recall": round(float(recall_score(actual, predicted, zero_division=0)), 6),
              "f1": round(float(f1_score(actual, predicted, zero_division=0)), 6),
              "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)}
    if probability is not None and len(np.unique(actual)) == 2:
        result["roc_auc"] = round(float(roc_auc_score(actual, probability)), 6)
        result["average_precision"] = round(float(average_precision_score(actual, probability)), 6)
    else:
        result["roc_auc"], result["average_precision"] = None, None
    return result


def _classification_candidates() -> dict[str, list[tuple[dict[str, Any], Callable[[], Any]]]]:
    return {
        "Logistic Regression": [({"C": c, "class_weight": w}, lambda c=c, w=w: LogisticRegression(C=c, class_weight=w, max_iter=2000, random_state=SEED)) for c, w in product([0.1, 1.0, 10.0], [None, "balanced"])],
        "Decision Tree Classifier": [({"max_depth": d, "min_samples_leaf": l, "class_weight": w}, lambda d=d, l=l, w=w: DecisionTreeClassifier(max_depth=d, min_samples_leaf=l, class_weight=w, random_state=SEED)) for d, l, w in [(4, 15, None), (6, 15, "balanced"), (8, 25, "balanced"), (10, 25, None)]],
        "Random Forest Classifier": [({"n_estimators": 180, "max_depth": d, "min_samples_leaf": l, "max_features": f, "class_weight": w}, lambda d=d, l=l, f=f, w=w: RandomForestClassifier(n_estimators=180, max_depth=d, min_samples_leaf=l, max_features=f, class_weight=w, random_state=SEED, n_jobs=1)) for d, l, f, w in [(10, 4, 0.7, None), (14, 4, 0.7, "balanced"), (None, 8, 1.0, None), (None, 8, 0.7, "balanced")]],
    }


def run_classification(panel: pd.DataFrame) -> dict[str, Any]:
    candidates, chosen, validation_rows = _classification_candidates(), {}, []
    for name, configurations in candidates.items():
        scored = []
        for params, factory in configurations:
            fold_scores = []
            for year in CV_YEARS:
                train, valid = panel[panel.year < year], panel[panel.year == year]
                model = _pipe(factory()); model.fit(train[ALL_FEATURES], train.growth_10pct)
                fold_scores.append(balanced_accuracy_score(valid.growth_10pct, model.predict(valid[ALL_FEATURES])))
            scored.append((float(np.mean(fold_scores)), params, factory))
        score, params, factory = max(scored, key=lambda item: item[0])
        chosen[name] = (params, factory, score)
        for year in CV_YEARS:
            train, valid = panel[panel.year < year], panel[panel.year == year]
            model = _pipe(factory()); model.fit(train[ALL_FEATURES], train.growth_10pct)
            probability = model.predict_proba(valid[ALL_FEATURES])[:, 1]
            validation_rows.append({"model": name, "fold_year": year, "n": len(valid), **classification_metrics(valid.growth_10pct.to_numpy(), (probability >= 0.5).astype(int), probability)})
    validation = pd.DataFrame(validation_rows)
    validation_summary = [{"model": name, "folds": len(group), "observations": int(group.n.sum()),
                           **{key: round(float(group[key].mean()), 6) for key in ["accuracy", "balanced_accuracy", "precision", "recall", "f1", "roc_auc", "average_precision"]}}
                          for name, group in validation.groupby("model", sort=False)]
    selected_name = max(validation_summary, key=lambda row: row["balanced_accuracy"])["model"]
    train, test = panel[panel.year < TEST_YEAR].copy(), panel[panel.year == TEST_YEAR].copy()
    test_results, selected_probability, selected_prediction = [], None, None
    for name, (params, factory, _) in chosen.items():
        model = _pipe(factory()); model.fit(train[ALL_FEATURES], train.growth_10pct)
        probability = model.predict_proba(test[ALL_FEATURES])[:, 1]; pred = (probability >= 0.5).astype(int)
        test_results.append({"model": name, "type": "trained", "hyperparameters": params, **classification_metrics(test.growth_10pct.to_numpy(), pred, probability)})
        if name == selected_name: selected_probability, selected_prediction = probability, pred
    dummy = DummyClassifier(strategy="most_frequent"); dummy.fit(np.zeros((len(train), 1)), train.growth_10pct)
    dummy_pred = dummy.predict(np.zeros((len(test), 1)))
    test_results.append({"model": "Majority-class dummy", "type": "baseline", "hyperparameters": {"strategy": "most_frequent"}, **classification_metrics(test.growth_10pct.to_numpy(), dummy_pred, None)})
    fpr, tpr, thresholds = roc_curve(test.growth_10pct, selected_probability)
    precision, recall, _ = precision_recall_curve(test.growth_10pct, selected_probability)
    selected_test = next(row for row in test_results if row["model"] == selected_name); majority = test_results[-1]
    return {
        "task": "Class 1 when target-month domestic traffic is at least 10% above the same month one year earlier",
        "threshold": 0.5, "growth_threshold": 0.10, "training_period": [str(panel.date.min().date()), "2024-12-01"],
        "validation_years": CV_YEARS, "test_period": ["2025-01-01", "2025-12-01"],
        "train_n": len(train), "test_n": len(test), "feature_count": len(ALL_FEATURES),
        "train_positive": int(train.growth_10pct.sum()), "test_positive": int(test.growth_10pct.sum()),
        "validation": validation_summary, "validation_folds": validation_rows, "test": test_results,
        "selected_model": selected_name, "selected_hyperparameters": chosen[selected_name][0],
        "beat_dummy_balanced_accuracy": bool(selected_test["balanced_accuracy"] > majority["balanced_accuracy"]),
        "roc_curve": [{"fpr": round(float(x), 6), "tpr": round(float(y), 6), "threshold": None if not np.isfinite(t) else round(float(t), 6)} for x, y, t in zip(fpr, tpr, thresholds)],
        "precision_recall_curve": [{"recall": round(float(r), 6), "precision": round(float(p), 6)} for r, p in zip(recall, precision)],
        "predicted_positive": int(selected_prediction.sum()),
    }


def run_clustering(latest: pd.DataFrame) -> dict[str, Any]:
    frame = latest.copy()
    features = ["log_domestic", "log_international", "domestic_growth", "seasonality_cv", "international_share", "active_months"]
    frame["log_domestic"], frame["log_international"] = np.log1p(frame.domestic), np.log1p(frame.international)
    X = StandardScaler().fit_transform(SimpleImputer(strategy="median").fit_transform(frame[features]))
    evaluations, fitted = [], {}
    for k in range(2, 7):
        model = KMeans(n_clusters=k, random_state=SEED, n_init=30); labels = model.fit_predict(X)
        sizes = np.bincount(labels, minlength=k)
        evaluations.append({"k": k, "inertia": round(float(model.inertia_), 4), "silhouette": round(float(silhouette_score(X, labels)), 6), "minimum_cluster_size": int(sizes.min())})
        fitted[k] = (model, labels)
    viable = [row for row in evaluations if row["minimum_cluster_size"] >= 5]; best = max(row["silhouette"] for row in viable)
    selected_k = min(row["k"] for row in viable if row["silhouette"] >= best - 0.02)
    _, labels = fitted[selected_k]; frame["cluster_raw"] = labels
    order = frame.groupby("cluster_raw").total.median().sort_values().index.tolist(); relabel = {raw: rank for rank, raw in enumerate(order)}
    frame["cluster"] = frame.cluster_raw.map(relabel)
    names = {2: ["Lower traffic", "Higher traffic"], 3: ["Lower traffic", "Regional traffic", "Major gateways"], 4: ["Small airports", "Regional airports", "Large airports", "Major gateways"], 5: ["Small airports", "Developing airports", "Regional airports", "Large airports", "Major gateways"], 6: ["Very small airports", "Small airports", "Developing airports", "Regional airports", "Large airports", "Major gateways"]}[selected_k]
    pca = PCA(n_components=2, random_state=SEED); components = pca.fit_transform(X)
    clusters = [{"id": int(c), "name": names[int(c)], "count": len(g), "median_domestic": int(g.domestic.median()),
                 "median_international": int(g.international.median()), "median_total": int(g.total.median()),
                 "median_growth": None if g.domestic_growth.dropna().empty else round(float(g.domestic_growth.median()), 4),
                 "median_seasonality_cv": round(float(g.seasonality_cv.median()), 4), "examples": g.nlargest(3, "total").airport.tolist()}
                for c, g in frame.groupby("cluster")]
    points = [{"airport": row.airport, "pc1": round(float(components[i, 0]), 6), "pc2": round(float(components[i, 1]), 6),
               "cluster": int(row.cluster), "domestic": int(row.domestic), "international": int(row.international)}
              for i, row in frame.reset_index(drop=True).iterrows()]
    loadings = [{"feature": name, "pc1": round(float(pca.components_[0, i]), 6), "pc2": round(float(pca.components_[1, i]), 6)} for i, name in enumerate(features)]
    selected_eval = next(row for row in evaluations if row["k"] == selected_k)
    return {"year": 2025, "n": len(frame), "k": selected_k, "silhouette": selected_eval["silhouette"],
            "selection_rule": "Minimum cluster size 5; within 0.02 of best silhouette, prefer smaller k",
            "features": features, "evaluations": evaluations, "clusters": clusters,
            "pca": {"explained_variance_ratio": [round(float(x), 6) for x in pca.explained_variance_ratio_],
                    "cumulative_explained_variance": [round(float(x), 6) for x in np.cumsum(pca.explained_variance_ratio_)],
                    "loadings": loadings, "points": points},
            "airport_clusters": {row.airport: int(row.cluster) for row in frame.itertuples()}}
