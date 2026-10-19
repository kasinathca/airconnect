"""Fast, offline data, model-output and website consistency tests."""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from pipeline import build_monthly_features, load_and_validate


def analysis():
    return json.loads((ROOT / "data/processed/analysis.json").read_text(encoding="utf-8"))


def test_external_sources_and_reconciliation():
    source = load_and_validate(ROOT)
    assert len(source["monthly"]) == 13599
    assert source["monthly"].airport.nunique() == 144
    assert set(source["yearly"].category) == {"domestic", "international"}
    assert all(len(value) == 64 for value in source["hashes"].values())


def test_exact_calendar_lags_and_no_target_leakage():
    monthly = pd.read_csv(ROOT / "data/external/india-aviation-stats/airport_monthly.csv")
    panel = build_monthly_features(monthly)
    assert len(panel) == 10444
    assert not panel.duplicated(["airport", "date"]).any()
    lookup = monthly.assign(date=pd.to_datetime(dict(year=monthly.year, month=monthly.month, day=1))).set_index(["airport", "date"]).passengers
    sample = panel.sample(100, random_state=37)
    for row in sample.itertuples():
        assert row.lag1 == lookup.loc[(row.airport, row.date - pd.offsets.MonthBegin(1))]
        assert row.lag12 == lookup.loc[(row.airport, row.date - pd.offsets.MonthBegin(12))]
    assert "target" not in analysis()["regression"]["features"]


def test_regression_metrics_and_common_test_rows():
    data = analysis()["regression"]
    records = data["predictions"]
    actual = np.array([r["actual"] for r in records], dtype=float)
    pred = np.array([r["selected_prediction"] for r in records], dtype=float)
    result = next(r for r in data["test"] if r["model"] == data["selected_model"])
    assert len(records) == data["test_n"]
    assert np.isfinite(pred).all() and (pred >= 0).all()
    assert abs(mean_absolute_error(actual, pred) - result["mae"]) < 0.02
    assert abs(np.sqrt(mean_squared_error(actual, pred)) - result["rmse"]) < 0.02
    assert abs(r2_score(actual, pred) - result["r2"]) < 0.0001
    assert all(row["model"] for row in data["test"])
    assert len({data["test_n"]}) == 1


def test_classification_counts_and_metrics():
    data = analysis()["classification"]
    assert data["growth_threshold"] == 0.10
    for row in data["test"]:
        assert row["tn"] + row["fp"] + row["fn"] + row["tp"] == data["test_n"]
        assert 0 <= row["accuracy"] <= 1
        assert 0 <= row["balanced_accuracy"] <= 1
    selected = next(row for row in data["test"] if row["model"] == data["selected_model"])
    assert selected["roc_auc"] is not None
    assert selected["tp"] + selected["fn"] == data["test_positive"]


def test_clustering_and_pca_dimensions():
    data = analysis()["clustering"]
    assert 2 <= data["k"] <= 6
    assert sum(row["count"] for row in data["clusters"]) == data["n"]
    assert len(data["pca"]["points"]) == data["n"]
    assert len(data["pca"]["loadings"]) == len(data["features"])
    assert all(0 <= value <= 1 for value in data["pca"]["explained_variance_ratio"])
    assert data["pca"]["cumulative_explained_variance"][1] <= 1


def test_generated_artifact_and_static_site():
    raw = (ROOT / "data/processed/analysis.json").read_text(encoding="utf-8")
    script = (ROOT / "site/assets/data.js").read_text(encoding="utf-8")
    assert script.endswith(";\n") and json.loads(raw)["metadata"]["version"] == "2.0.0"
    html = (ROOT / "site/index.html").read_text(encoding="utf-8")
    app = (ROOT / "site/assets/app.js").read_text(encoding="utf-8")
    assert all(token in html for token in ["page-overview", "page-explorer", "page-models", "page-method", "ml-regression", "ml-classification", "ml-clustering"])
    assert all(token in app for token in ["renderTable", "renderMap", "confusionMatrix", "rocChart", "pcaChart", "downloadCSV"])
    assert "data.js" in html and "app.js" in html and "Kubicek" in html
    assert not any(token in html for token in ["https://cdn.", "googletagmanager", "google-analytics"])
