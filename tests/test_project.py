"""Fast, network-free tests for project input and trained output."""
import sys, json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from build import run


def test_input_rows_and_uniqueness():
    df=pd.read_csv(ROOT/'data/raw/airport_yearly_2022_2025.csv')
    assert len(df)==614
    assert sorted(df.year.unique().tolist())==[2022,2023,2024,2025]
    assert not df.duplicated(['year','airport','category']).any()
    assert df.passengers.ge(0).all()


def test_national_totals():
    df=pd.read_csv(ROOT/'data/raw/airport_yearly_2022_2025.csv')
    expected=pd.read_csv(ROOT/'data/raw/national_2016_2025.csv').set_index('year')
    for year in range(2022,2026):
        actual=df[df.year==year].groupby('category').passengers.sum()
        assert int(actual.domestic)==int(expected.loc[year,'domestic'])
        assert int(actual.international)==int(expected.loc[year,'international'])


def test_output_and_model_consistency():
    d=json.loads((ROOT/'data/processed/analysis.json').read_text())
    assert d['clustering']['n']==129
    assert sum(c['count'] for c in d['clusters'])==129
    assert -1 <= d['clustering']['silhouette'] <= 1
    assert d['regression']['train_year']!=d['regression']['test_year']
    assert d['regression']['train_n']>=100
    p=d['regression']['predictions']
    assert len(p)==d['regression']['test_n']==116
    assert all(np.isfinite(r['predicted']) and r['predicted']>=0 for r in p)
    from sklearn.metrics import mean_absolute_error
    actual=[x['actual'] for x in p]
    predicted=[x['predicted'] for x in p]
    assert abs(mean_absolute_error(actual,predicted)-d['regression']['forest']['mae'])<1


def test_generation_determinism():
    before=(ROOT/'site/assets/data.js').read_bytes()
    run()
    after=(ROOT/'site/assets/data.js').read_bytes()
    assert before==after


def test_static_site_and_source_disclosure():
    h=(ROOT/'site/index.html').read_text()
    js=(ROOT/'site/assets/app.js').read_text()
    assert all(x in h for x in ['page-overview','page-explorer','page-models','page-method'])
    assert all(x in js for x in ['renderTable','renderMap','trend','downloadCSV'])
    assert 'data.js' in h and 'app.js' in h
    assert 'Kubicek' in h
    assert not any(s in h for s in ['https://cdn.', 'googletagmanager', 'google-analytics'])
