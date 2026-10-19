/* AirConnect India: offline, dependency-free browser interface. */
(() => {
  'use strict';
  const D = window.AIRCONNECT_DATA;
  if (!D) { document.body.textContent = 'Project data is missing. Please restore site/assets/data.js and refresh.'; return; }
  const $ = id => document.getElementById(id);
  const num = n => Math.round(Number(n)).toLocaleString('en-IN');
  const millions = n => `${(n / 1e6).toFixed(1)}M`;
  const pct = n => `${(100 * n).toFixed(1)}%`;
  const safe = s => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const color = ['#abb9c6','#387cab','#123f6d'];
  const state = {year:2025,group:'all',search:'',limit:20};
  const byYear = year => D.airports.filter(a=>a.year===year);
  const official = D.government;
  const latest = D.historical.find(x=>x.year===2025);
  const earliest = D.historical.find(x=>x.year===2016);

  function metric(label, value, foot, title, blue=false) {
    return `<div class="metric ${blue?'blue':''}" tabindex="0" title="${safe(title)}"><em aria-hidden="true">ⓘ</em><div class="metric-label">${safe(label)}</div><div class="metric-value">${value}</div><div class="metric-foot">${safe(foot)}</div></div>`;
  }
  $('metrics').innerHTML = [
   metric('Operational facilities',`${official.operational_2014} → ${official.operational_2026}`,'2014 versus 7 July 2026','Ministry of Civil Aviation figure. The facilities include airports and other operational aviation facilities. Not directly comparable to airport records reporting traffic.',true),
   metric('Domestic movements',millions(latest.domestic),'Calendar year 2025','Total domestic passenger movements at reporting airports, arrivals plus departures.'),
   metric('International movements',millions(latest.international),'Calendar year 2025','Total international airport passenger movements, arrivals plus departures.'),
   metric('Domestic growth',`+${((latest.domestic / earliest.domestic-1)*100).toFixed(1)}%`,'2016 to 2025','Percent change in the annual DGCA-derived domestic passenger movement series; this is not the percent growth in airport count.')
  ].join('');

  // National annual SVG series chart, with native browser hover/focus descriptions.
  function trend() {
    const data=D.historical;
    const width=660,height=292,L=59,R=25,T=22,B=42;
    const max=Math.ceil(Math.max(...data.map(r=>r.domestic))/5e7)*5e7;
    const sx=i=>L+i*(width-L-R)/(data.length-1);
    const sy=v=>height-B-v/max*(height-T-B);
    const grid=[0,.25,.5,.75,1].map(n=>{
      const y=sy(max*n);return `<line x1="${L}" y1="${y}" x2="${width-R}" y2="${y}" stroke="#e1e7eb" stroke-width="1"/><text x="${L-12}" y="${y+4}" text-anchor="end" fill="#73828e" font-size="11">${(max*n/1e6).toFixed(0)}</text>`;
    }).join('');
    const labels=data.map((d,i)=> `<text x="${sx(i)}" y="${height-17}" font-size="10" text-anchor="middle" fill="#6d7985">${d.year}</text>`).join('');
    const points=key=>data.map((d,i)=>`${sx(i)},${sy(d[key])}`).join(' ');
    const dots=(key,col)=>data.map((d,i)=>`<circle tabindex="0" cx="${sx(i)}" cy="${sy(d[key])}" r="4.1" fill="${col}" stroke="white" stroke-width="1" aria-label="${d.year}: ${key} ${num(d[key])} movements"><title>${d.year} · ${key}: ${num(d[key])} passenger movements</title></circle>`).join('');
    $('trendChart').innerHTML=`<svg viewBox="0 0 ${width} ${height}" role="img" aria-label="National domestic and international airport passenger movements 2016 to 2025"><text x="${L}" y="12" font-size="10" fill="#8897a5">MILLION MOVEMENTS</text>${grid}${labels}<polyline points="${points('domestic')}" fill="none" stroke="#0067b8" stroke-width="3" stroke-linejoin="round"/><polyline points="${points('international')}" fill="none" stroke="#48858a" stroke-width="2.7" stroke-linejoin="round"/>${dots('domestic','#0067b8')}${dots('international','#48858a')}</svg>`;
  }
  trend();

  function switchPage(page, updateHash=true) {
    const pages=['overview','explorer','models','method'];
    if(!pages.includes(page))page='overview';
    for(const p of pages) {
      const s=$('page-'+p);s.hidden=(p!==page);s.classList.toggle('active',p===page);
    }
    for(const button of document.querySelectorAll('[data-page]')){
      const active=button.dataset.page===page;
      button.classList.toggle('active',active);
      if(active)button.setAttribute('aria-current','page'); else button.removeAttribute('aria-current');
    }
    if(updateHash)history.replaceState(null,'','#'+page);
    window.scrollTo(0,0);
    $('liveRegion').textContent='Showing '+page.replace('method','methodology')+' section.';
  }
  document.querySelectorAll('[data-page]').forEach(b=>b.addEventListener('click',()=>switchPage(b.dataset.page)));
  document.querySelector('.brand').addEventListener('click',e=>{e.preventDefault();switchPage('overview');});
  window.addEventListener('hashchange',()=>switchPage(location.hash.replace('#',''),false));
  switchPage(location.hash.replace('#',''),false);

  function filtered() {
    let rows=byYear(state.year);
    if(state.year===2025 && state.group!=='all')rows=rows.filter(r=>String(r.cluster)===state.group);
    if(state.search)rows=rows.filter(r=>r.code.toUpperCase().includes(state.search.toUpperCase()));
    return rows.sort((a,b)=>b.total-a.total);
  }
  function renderTable(){
    const rows=filtered(),subset=rows.slice(0,state.limit);
    $('airportRows').innerHTML=subset.length ? subset.map(r=>`<tr title="${safe(r.code)} · ${state.year}: domestic ${num(r.domestic)}, international ${num(r.international)} recorded movements"><td><strong>${safe(r.code)}</strong><small>${state.year===2025 && r.cluster!==undefined ? safe(D.clusters[r.cluster].name) : 'Airport IATA code'}</small></td><td class="numeric">${num(r.domestic)}</td><td class="numeric">${num(r.international)}</td><td class="numeric"><strong>${num(r.total)}</strong></td></tr>`).join('') : '<tr><td colspan="4">No airports match these filters.</td></tr>';
    $('recordCount').textContent=`Showing ${Math.min(rows.length,state.limit)} of ${rows.length} airports`;
    $('tableSubtitle').textContent=`${state.year} records · arrivals and departures combined`;
    $('showMore').disabled=state.limit>=rows.length;
    $('clusterFilter').disabled=state.year!==2025;
    renderMap();
  }
  function renderMap() {
    const rows=filtered().filter(r=>Number.isFinite(r.lat)&&Number.isFinite(r.lon));
    const width=660,height=630;
    const toX=lon=>(lon-67.5)/(98.2-67.5)*width;
    const toY=lat=>(37.7-lat)/(37.7-6.4)*height;
    const max=Math.max(1,...rows.map(r=>r.total));
    const marks=rows.slice().sort((a,b)=>b.total-a.total).map(r=>{
      const cluster=state.year===2025&&r.cluster!==undefined?r.cluster:null;
      const fill=cluster===null?'#557b98':color[cluster];
      const radius=Math.min(7,Math.max(3.2,2.8+3.7*Math.sqrt(r.total/max)));
      const label=`${r.code}, ${state.year}: ${num(r.total)} passenger movements`;
      return `<circle class="airport-marker" role="button" tabindex="0" data-airport="${safe(r.code)}" aria-label="Filter to ${safe(label)}" cx="${toX(r.lon).toFixed(2)}" cy="${toY(r.lat).toFixed(2)}" r="${radius.toFixed(2)}" fill="${fill}" fill-opacity=".90" stroke="white" stroke-width="1.1"><title>${safe(label)} — click or press Enter to isolate</title></circle>`;
    }).join('');
    $('airportMap').innerHTML=`<svg viewBox="0 0 660 630" role="group" aria-label="Simplified outline map with ${rows.length} airport markers"><path d="${window.INDIA_MAP_PATH||''}" fill="#ecf1f5" stroke="#b6c6d2" stroke-width="1.65" stroke-linejoin="round"/><g>${marks}</g><text x="17" y="605" fill="#98a7b4" font-size="11">Geographic illustration · positions approximate</text></svg>`;
    $('mapCount').textContent=`${rows.length} mapped / ${filtered().length} records`;
    $('airportMap').querySelectorAll('[data-airport]').forEach(n=>{
      function activate(){state.search=n.dataset.airport;$('airportSearch').value=state.search;state.limit=20;renderTable();$('liveRegion').textContent='Showing '+state.search+' airport.';}
      n.addEventListener('click',activate);
      n.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();activate();}});
    });
  }
  $('exploreYear').addEventListener('change',e=>{state.year=Number(e.target.value);state.limit=20;state.group='all';$('clusterFilter').value='all';renderTable();});
  $('clusterFilter').addEventListener('change',e=>{state.group=e.target.value;state.limit=20;renderTable();});
  $('airportSearch').addEventListener('input',e=>{state.search=e.target.value.trim().replace(/[^a-z0-9]/gi,'').slice(0,5);state.limit=20;renderTable();});
  $('resetExplorer').addEventListener('click',()=>{state.year=2025;state.group='all';state.search='';state.limit=20;$('exploreYear').value='2025';$('clusterFilter').value='all';$('airportSearch').value='';renderTable();});
  $('showMore').addEventListener('click',()=>{state.limit+=20;renderTable();});
  $('downloadCSV').addEventListener('click',()=>{
    const rows=filtered();const header='year,airport,domestic_movements,international_movements,total_movements';
    const csv=[header,...rows.map(x=>[x.year,x.code,x.domestic,x.international,x.total].join(','))].join('\r\n');
    const blob=new Blob(['\uFEFF'+csv],{type:'text/csv;charset=utf-8'});
    const url=URL.createObjectURL(blob);const link=document.createElement('a');link.href=url;link.download=`airconnect_${state.year}_airports.csv`;link.click();URL.revokeObjectURL(url);
    $('liveRegion').textContent='Airport CSV export started.';
  });
  renderTable();

  const K=D.clustering;
  $('clusterMetrics').innerHTML=[
   metric('Airports clustered',num(K.n),'2025, domestic reporting records','Airport-level 2025 records with at least one domestic passenger movement.',true),
   metric('Number of groups',num(K.k),'Preselected k = 3','K-Means is an unsupervised algorithm; there are no ground-truth class labels.'),
   metric('Silhouette Score',K.silhouette.toFixed(3),'Higher is better (−1 to 1)','Silhouette Score measures cohesion and separation of the clusters for the scaled features.'),
   metric('Feature dimensions','2','Annual passenger counts','Log-transformed domestic and international annual passenger movements, then standardized.')
  ].join('');
  $('clusterBars').innerHTML=D.clusters.map(c=>`<div class="cluster-row" title="${safe(c.name)}: ${c.count} airports in this group"><div class="cluster-caption"><strong>${safe(c.name)}</strong><span>${c.count} airports</span></div><div class="bar-track"><div class="bar-fill" style="width:${(c.count/K.n*100).toFixed(2)}%;background:${color[c.id]}"></div></div></div>`).join('');
  $('clusterDetails').innerHTML=D.clusters.map(c=>`<div class="cluster-detail" title="Cluster medians, computed on 2025 airport records"><h3><i class="dot" style="background:${color[c.id]}"></i>${safe(c.name)}</h3><p>Median domestic: <strong>${num(c.median_domestic)}</strong></p><p>Median international: <strong>${num(c.median_international)}</strong></p><p>Examples: ${c.examples.map(safe).join(' · ')}</p></div>`).join('');
  const R=D.regression, f=R.forest,b=R.baseline;
  const show=n=>Number(n).toLocaleString('en-IN',{maximumFractionDigits:0});
  const winner=(x,y,lower=true)=>lower?x<y:x>y;
  $('modelMetrics').innerHTML=`<div class="score-table"><div class="score-header"><span>Metric</span><span>Random Forest</span><span>Prior-year baseline</span></div>
    <div class="score-row"><span>MAE ↓</span><span title="Mean Absolute Error: average absolute passenger difference">${show(f.mae)}</span><strong title="Baseline Mean Absolute Error">${show(b.mae)}</strong></div>
    <div class="score-row"><span>RMSE ↓</span><span title="Root Mean Squared Error: penalises larger prediction errors">${show(f.rmse)}</span><strong title="Baseline Root Mean Squared Error">${show(b.rmse)}</strong></div>
    <div class="score-row"><span>R² ↑</span><span title="Coefficient of determination on unseen 2025 examples">${f.r2.toFixed(4)}</span><strong title="Baseline coefficient of determination">${b.r2.toFixed(4)}</strong></div>
    <p class="score-note">Training examples: <strong>${R.train_n}</strong> (2024). Test examples: <strong>${R.test_n}</strong> (2025). <strong>${winner(b.mae,f.mae)?'The simple baseline has lower average error.':'The Random Forest has lower average error.'}</strong> No randomised train/test shuffle was used.</p></div>`;
  const preds=R.predictions.slice(0,7);
  const highest=Math.max(...preds.flatMap(p=>[p.actual,p.predicted]));
  $('predictionChart').innerHTML=preds.map(p=>`<div class="pred-outer" title="${safe(p.airport)}: actual ${num(p.actual)}; Random Forest ${num(p.predicted)} passenger movements"><div class="pred-head"><strong>${safe(p.airport)}</strong><span>${millions(p.actual)} actual</span></div><div class="pred-pair"><div style="width:${(p.actual/highest*100).toFixed(2)}%"></div><div class="model-value" style="width:${(p.predicted/highest*100).toFixed(2)}%"></div></div></div>`).join('')+`<div class="pred-leg"><span><b></b>Actual</span><span><b class="pale"></b>Random Forest</span></div>`;
})();
