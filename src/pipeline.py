"""Validated, leakage-safe feature construction for AirConnect India v2.0."""
from __future__ import annotations

from pathlib import Path
import hashlib

import numpy as np
import pandas as pd


UPSTREAM_COMMIT = "bce8fc78f2be1de88154c1d8e62d13ffc0d8e171"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_and_validate(root: Path) -> dict:
    source = root / "data" / "external" / "india-aviation-stats"
    monthly_path = source / "airport_monthly.csv"
    yearly_path = source / "airport_yearly.csv"
    quarterly_path = source / "airport_international_quarterly.csv"
    for path in (monthly_path, yearly_path, quarterly_path, source / "LICENSE"):
        if not path.exists():
            raise FileNotFoundError(f"Required upstream source is missing: {path}")

    monthly = pd.read_csv(monthly_path)
    yearly = pd.read_csv(yearly_path)
    quarterly = pd.read_csv(quarterly_path)
    required = {
        "monthly": (monthly, ["year", "month", "airport", "passengers", "departures", "arrivals"]),
        "yearly": (yearly, ["year", "airport", "category", "passengers"]),
        "quarterly": (quarterly, ["year", "quarter", "airport", "passengers", "departures", "arrivals"]),
    }
    for name, (frame, columns) in required.items():
        if frame.columns.tolist() != columns:
            raise ValueError(f"Unexpected {name} schema: {frame.columns.tolist()}")
        if frame[columns].isna().any().any():
            raise ValueError(f"Missing core values in {name}")
        if (frame["passengers"] < 0).any():
            raise ValueError(f"Negative passenger values in {name}")
    if monthly.duplicated(["year", "month", "airport"]).any():
        raise ValueError("Duplicate airport-month keys")
    if yearly.duplicated(["year", "airport", "category"]).any():
        raise ValueError("Duplicate airport-year-category keys")
    if quarterly.duplicated(["year", "quarter", "airport"]).any():
        raise ValueError("Duplicate international airport-quarter keys")
    if not monthly["month"].between(1, 12).all() or not quarterly["quarter"].between(1, 4).all():
        raise ValueError("Invalid month or quarter")
    if not (monthly["passengers"] == monthly["departures"] + monthly["arrivals"]).all():
        raise ValueError("Monthly passenger totals do not equal departures plus arrivals")
    if not (quarterly["passengers"] == quarterly["departures"] + quarterly["arrivals"]).all():
        raise ValueError("Quarterly passenger totals do not equal departures plus arrivals")

    complete_years = sorted(
        int(year) for year in monthly["year"].unique()
        if year <= 2025 and monthly.loc[monthly.year == year, "month"].nunique() == 12
    )
    monthly_totals = monthly[monthly.year.isin(complete_years)].groupby("year")["passengers"].sum()
    yearly_domestic = yearly[(yearly.category == "domestic") & yearly.year.isin(complete_years)].groupby("year")["passengers"].sum()
    if not monthly_totals.equals(yearly_domestic):
        mismatch = pd.concat([monthly_totals.rename("monthly"), yearly_domestic.rename("yearly")], axis=1)
        raise ValueError(f"Monthly/yearly domestic reconciliation failed:\n{mismatch}")

    return {
        "monthly": monthly, "yearly": yearly, "quarterly": quarterly,
        "hashes": {monthly_path.name: sha256(monthly_path), yearly_path.name: sha256(yearly_path), quarterly_path.name: sha256(quarterly_path)},
    }


def build_monthly_features(monthly: pd.DataFrame) -> pd.DataFrame:
    """Build exact-calendar lags; missing calendar observations remain NaN."""
    base = monthly[monthly.year <= 2025].copy()
    base["date"] = pd.to_datetime(dict(year=base.year, month=base.month, day=1))
    base = base[["airport", "date", "year", "month", "passengers"]].rename(columns={"passengers": "target"})
    base = base.sort_values(["airport", "date"]).reset_index(drop=True)
    for lag in range(1, 14):
        prior = base[["airport", "date", "target"]].copy()
        prior["date"] = prior["date"] + pd.offsets.MonthBegin(lag)
        prior = prior.rename(columns={"target": f"lag{lag}"})
        base = base.merge(prior, on=["airport", "date"], how="left", validate="one_to_one")

    base["rolling_mean_3"] = base[[f"lag{i}" for i in range(1, 4)]].mean(axis=1)
    base["rolling_mean_6"] = base[[f"lag{i}" for i in range(1, 7)]].mean(axis=1)
    base["rolling_mean_12"] = base[[f"lag{i}" for i in range(1, 13)]].mean(axis=1)
    base["observed_prior_6"] = base[[f"lag{i}" for i in range(1, 7)]].notna().sum(axis=1)
    base["observed_prior_12"] = base[[f"lag{i}" for i in range(1, 13)]].notna().sum(axis=1)
    base["growth_1m"] = np.where(base.lag2 > 0, base.lag1 / base.lag2 - 1, np.nan)
    base["growth_yoy_lag"] = np.where(base.lag13 > 0, base.lag1 / base.lag13 - 1, np.nan)
    base["growth_1m"] = base["growth_1m"].clip(-1, 5)
    base["growth_yoy_lag"] = base["growth_yoy_lag"].clip(-1, 5)
    base["month_sin"] = np.sin(2 * np.pi * base.month / 12)
    base["month_cos"] = np.cos(2 * np.pi * base.month / 12)
    base["time_index"] = (base.year - 2015) * 12 + base.month
    base["growth_10pct"] = np.where(base.lag12 > 0, (base.target >= 1.10 * base.lag12).astype(int), np.nan)
    eligible = base.target.notna() & base.lag1.notna() & base.lag12.notna() & base.growth_10pct.notna()
    panel = base.loc[eligible].copy()
    panel["target"] = panel.target.astype(int)
    panel["growth_10pct"] = panel.growth_10pct.astype(int)
    return panel.sort_values(["date", "airport"]).reset_index(drop=True)


def latest_airport_features(monthly: pd.DataFrame, yearly: pd.DataFrame) -> pd.DataFrame:
    annual = yearly[yearly.year.isin([2024, 2025])].pivot_table(index=["year", "airport"], columns="category", values="passengers", aggfunc="sum").reset_index()
    annual.columns.name = None
    annual["domestic"] = annual.get("domestic", 0).fillna(0)
    annual["international"] = annual.get("international", 0).fillna(0)
    current = annual[(annual.year == 2025) & (annual.domestic > 0)].copy()
    prior = annual[annual.year == 2024][["airport", "domestic"]].rename(columns={"domestic": "domestic_2024"})
    current = current.merge(prior, on="airport", how="left", validate="one_to_one")
    current["domestic_growth"] = np.where(current.domestic_2024 > 0, current.domestic / current.domestic_2024 - 1, np.nan).clip(-1, 5)
    months = monthly[monthly.year == 2025].groupby("airport").agg(active_months=("month", "nunique"), monthly_mean=("passengers", "mean"), monthly_std=("passengers", "std")).reset_index()
    months["seasonality_cv"] = np.where(months.monthly_mean > 0, months.monthly_std / months.monthly_mean, 0)
    current = current.merge(months[["airport", "active_months", "seasonality_cv"]], on="airport", how="left")
    current["total"] = current.domestic + current.international
    current["international_share"] = np.where(current.total > 0, current.international / current.total, 0)
    return current.reset_index(drop=True)
