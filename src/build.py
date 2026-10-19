"""Offline, deterministic model training and static website data generation."""
from pathlib import Path
import json, csv, math
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, silhouette_score
from sklearn.preprocessing import StandardScaler
from seed_data import unpack

ROOT=Path(__file__).resolve().parents[1]
SEED=37


def run():
    unpack(ROOT/'data'/'raw')
    source=pd.read_csv(ROOT/'data/raw/airport_yearly_2022_2025.csv')
    totals=pd.read_csv(ROOT/'data/raw/national_2016_2025.csv')
    assert not source.duplicated(['year','airport','category']).any()
    assert (source.passengers >=0).all()
    assert set(source.category)=={'domestic','international'}
    assert len(source)==614, f'Unexpected source rows: {len(source)}'
    for year in range(2022,2026):
        s=source[source.year==year].groupby('category').passengers.sum()
        row=totals[totals.year==year].iloc[0]
        assert s['domestic']==row.domestic and s['international']==row.international
    pivot=source.pivot_table(index=['year','airport'],columns='category',values='passengers',aggfunc='sum').reset_index()
    pivot.columns.name=None
    for column in ['domestic','international']:
        pivot[column]=pivot[column].fillna(0).astype(int)
    pivot['total']=pivot.domestic+pivot.international
    pivot['intl_share']=np.where(pivot.total>0,pivot.international/pivot.total,0)
    # Train K-Means on 2025 cross-sectional traffic. Features intentionally count-based.
    latest=pivot[(pivot.year==2025)&(pivot.domestic>0)].copy().reset_index(drop=True)
    features=np.log1p(latest[['domestic','international']].to_numpy(float))
    scaler=StandardScaler().fit(features)
    X=scaler.transform(features)
    cluster_model=KMeans(n_clusters=3,random_state=SEED,n_init=20)
    latest['cluster_raw']=cluster_model.fit_predict(X)
    ordering=latest.groupby('cluster_raw')['total'].median().sort_values().index.tolist()
    relabel={raw:i for i,raw in enumerate(ordering)}
    latest['cluster']=latest.cluster_raw.map(relabel)
    silhouette=float(silhouette_score(X,latest.cluster_raw))
    cluster_meta=[]
    for i,group in latest.groupby('cluster'):
        cluster_meta.append({"id":int(i),"name":["Lower traffic","Intermediate traffic","Major gateways"][int(i)],"count":len(group),
            "median_domestic":int(group.domestic.median()),"median_international":int(group.international.median()),
            "median_total":int(group.total.median()),"examples":group.nlargest(3,'total').airport.tolist()})

    # Year-ahead regression, 2024 as training target and 2025 strictly unseen.
    # Retains only airports with explicit domestic observations for all required years.
    domest=source[source.category=='domestic'].pivot(index='airport',columns='year',values='passengers')
    rows=[]
    for airport,values in domest.iterrows():
        for target_year in [2024,2025]:
            y1,y2=values.get(target_year-1),values.get(target_year-2)
            target=values.get(target_year)
            if pd.notna(y1) and pd.notna(y2) and pd.notna(target) and y1>0:
                rows.append(dict(airport=airport,year=target_year,lag1=int(y1),lag2=int(y2),target=int(target)))
    reg=pd.DataFrame(rows)
    tr=reg[reg.year==2024].copy()
    te=reg[reg.year==2025].copy()
    cols=['lag1','lag2']
    Xtrain=np.log1p(tr[cols].to_numpy(float))
    Xtest=np.log1p(te[cols].to_numpy(float))
    model=RandomForestRegressor(n_estimators=120,max_depth=9,min_samples_leaf=2,random_state=SEED,n_jobs=1)
    model.fit(Xtrain,np.log1p(tr.target.to_numpy()))
    predictions=np.expm1(model.predict(Xtest))
    predictions=np.clip(predictions,0,None)
    actual=te.target.to_numpy()
    baseline=te.lag1.to_numpy()
    def metrics(a,b):
        return {'mae':round(float(mean_absolute_error(a,b)),2),
            'rmse':round(float(np.sqrt(mean_squared_error(a,b))),2),
            'r2':round(float(r2_score(a,b)),4)}
    regression={'train_year':2024,'test_year':2025,'train_n':len(tr),'test_n':len(te),
        'model':'Random Forest regression','features':['Prior-year domestic passengers','Two-years-prior domestic passengers'],
        'forest':metrics(actual,predictions),'baseline':metrics(actual,baseline),
        'feature_importances':[round(float(x),4) for x in model.feature_importances_],
        'predictions': sorted([{'airport':str(r.airport),'actual':int(r.target),'predicted':round(float(p)),
                                'baseline':int(r.lag1)} for r,p in zip(te.itertuples(),predictions)],
                               key=lambda x:x['actual'],reverse=True)}
    coords=pd.read_csv(ROOT/'data/raw/airport_coordinates_2025.csv').set_index('airport')
    rec=[]
    for r in pivot.itertuples():
        code=r.airport
        if r.year==2025 and code in set(latest.airport):
            cluster=int(latest.loc[latest.airport==code,'cluster'].iloc[0])
        else: cluster=None
        item={'year':int(r.year),'code':code,'domestic':int(r.domestic),'international':int(r.international),'total':int(r.total),
              'share':round(float(r.intl_share),6)}
        if cluster is not None:item['cluster']=cluster
        if code in coords.index:
            item['lat']=round(float(coords.loc[code,'latitude']),3)
            item['lon']=round(float(coords.loc[code,'longitude']),3)
        rec.append(item)
    dataset={
     'metadata':{'name':'AirConnect India','version':'1.0.0','traffic_scope':'airport passenger movements (arrival + departure)',
            'years_airport': [2022,2023,2024,2025], 'national_years':[2016,2025],
            'source':'Kubicek (2026), cleaned DGCA aviation data','airport_coord_source':'Brandon Himpfen airports dataset (MIT)',
            'reporting_airports_2025':len(latest),'coordinates_coverage_2025':int(latest.airport.isin(coords.index).sum()),
            'random_seed':SEED},
     'historical':totals.to_dict('records'),
     'government':{'operational_2014':74,'operational_2026':165,'as_of':'7 July 2026',
                    'note':'All operational aviation facilities, which may include heliports and water aerodromes; NOT equivalent to DGCA reporting airport counts.'},
     'airports':rec,'clusters':cluster_meta,'clustering':{'k':3,'n':len(latest),'silhouette':round(silhouette,4),
                            'features':['log(1+domestic passengers)','log(1+international passengers)'],'standardized':True},
     'regression':regression}
    (ROOT/'data/processed').mkdir(parents=True,exist_ok=True)
    (ROOT/'data/processed/analysis.json').write_text(json.dumps(dataset,indent=2,ensure_ascii=False),encoding='utf-8')
    (ROOT/'site/assets/data.js').write_text('/* Generated from verified DGCA-derived rows; do not hand-edit. */\nwindow.AIRCONNECT_DATA = '+json.dumps(dataset,separators=(',',':'))+';\n',encoding='utf-8')
    pd.DataFrame(rec).to_csv(ROOT/'data/processed/airport_features.csv',index=False)
    print(json.dumps({'source_rows':len(source),'airport_year_rows':len(pivot),'cluster_score':silhouette,'clusters':cluster_meta,
                      'regression':{k:v for k,v in regression.items() if k!='predictions'},'coordinates':len(coords)},indent=2))
    return dataset

if __name__=='__main__':run()
