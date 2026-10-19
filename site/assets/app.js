/* AirConnect India v2.0: offline, dependency-free research interface. */
(() => {
  'use strict';
  const D=window.AIRCONNECT_DATA,$=id=>document.getElementById(id);
  if(!D){document.body.textContent='Project data is missing. Restore site/assets/data.js and refresh.';return;}
  const num=n=>Math.round(Number(n)).toLocaleString('en-IN');
  const dec=(n,d=3)=>Number(n).toLocaleString('en-IN',{minimumFractionDigits:d,maximumFractionDigits:d});
  const millions=n=>`${(n/1e6).toFixed(1)}M`,pct=n=>`${(100*n).toFixed(1)}%`;
  const safe=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const colors=['#a8b8c6','#4f86ac','#23628f','#123f6d','#557b80','#836f55'];
  const state={year:2025,group:'all',search:'',limit:20};
  const latest=D.historical.find(x=>x.year===2025),earliest=D.historical.find(x=>x.year===2016),official=D.government;
  const byYear=year=>D.airports.filter(a=>a.year===year);

  function metric(label,value,foot,tip,blue=false){return `<div class="metric ${blue?'blue':''}" tabindex="0" data-tooltip="${safe(tip)}"><em aria-hidden="true">ⓘ</em><div class="metric-label">${safe(label)}</div><div class="metric-value">${value}</div><div class="metric-foot">${safe(foot)}</div></div>`;}
  $('metrics').innerHTML=[
    metric('Operational facilities',`${official.operational_2014} → ${official.operational_2026}`,'2014 versus 7 July 2026','Ministry of Civil Aviation count; not identical to traffic-reporting airports.',true),
    metric('Domestic movements',millions(latest.domestic),'Calendar year 2025','Arrivals plus departures at reporting airports.'),
    metric('International movements',millions(latest.international),'Calendar year 2025','International arrivals plus departures at reporting airports.'),
    metric('Domestic growth',`+${((latest.domestic/earliest.domestic-1)*100).toFixed(1)}%`,'2016 to 2025','Change in passenger movements, not airport count.')
  ].join('');

  function trend(){
    const data=D.historical,w=660,h=292,L=59,R=25,T=22,B=42,max=Math.ceil(Math.max(...data.map(r=>r.domestic))/5e7)*5e7;
    const sx=i=>L+i*(w-L-R)/(data.length-1),sy=v=>h-B-v/max*(h-T-B);
    const grid=[0,.25,.5,.75,1].map(n=>`<line x1="${L}" y1="${sy(max*n)}" x2="${w-R}" y2="${sy(max*n)}" stroke="#e1e7eb"/><text x="${L-12}" y="${sy(max*n)+4}" text-anchor="end" fill="#73828e" font-size="11">${(max*n/1e6).toFixed(0)}</text>`).join('');
    const labels=data.map((d,i)=>`<text x="${sx(i)}" y="${h-17}" font-size="10" text-anchor="middle" fill="#6d7985">${d.year}</text>`).join('');
    const points=k=>data.map((d,i)=>`${sx(i)},${sy(d[k])}`).join(' ');
    const dots=(k,c)=>data.map((d,i)=>`<circle tabindex="0" cx="${sx(i)}" cy="${sy(d[k])}" r="4.1" fill="${c}" stroke="white" data-tooltip="${d.year} ${k}: ${num(d[k])} passenger movements"/>`).join('');
    $('trendChart').innerHTML=`<svg viewBox="0 0 ${w} ${h}" role="img" aria-label="National domestic and international passenger movements from 2016 to 2025"><text x="${L}" y="12" font-size="10" fill="#8897a5">MILLION MOVEMENTS</text>${grid}${labels}<polyline points="${points('domestic')}" fill="none" stroke="#0067b8" stroke-width="3"/><polyline points="${points('international')}" fill="none" stroke="#48858a" stroke-width="2.7"/>${dots('domestic','#0067b8')}${dots('international','#48858a')}</svg>`;
  }
  trend();

  function switchPage(page,updateHash=true){
    const pages=['overview','explorer','models','method'];if(!pages.includes(page))page='overview';
    pages.forEach(p=>{const section=$(`page-${p}`);section.hidden=p!==page;section.classList.toggle('active',p===page);});
    document.querySelectorAll('[data-page]').forEach(button=>{const active=button.dataset.page===page;button.classList.toggle('active',active);active?button.setAttribute('aria-current','page'):button.removeAttribute('aria-current');});
    if(updateHash)history.replaceState(null,'',`#${page}`);window.scrollTo(0,0);$('liveRegion').textContent=`Showing ${page==='method'?'methodology':page} section.`;
  }
  document.querySelectorAll('[data-page]').forEach(b=>b.addEventListener('click',()=>switchPage(b.dataset.page)));
  document.querySelector('.brand').addEventListener('click',e=>{e.preventDefault();switchPage('overview');});
  window.addEventListener('hashchange',()=>switchPage(location.hash.slice(1),false));switchPage(location.hash.slice(1),false);

  function filtered(){let rows=byYear(state.year);if(state.year===2025&&state.group!=='all')rows=rows.filter(r=>String(r.cluster)===state.group);if(state.search)rows=rows.filter(r=>r.code.includes(state.search.toUpperCase()));return rows.sort((a,b)=>b.total-a.total);}
  function renderTable(){
    const rows=filtered(),subset=rows.slice(0,state.limit),clusters=D.clustering.clusters;
    $('airportRows').innerHTML=subset.length?subset.map(r=>`<tr data-tooltip="${r.code} in ${state.year}: domestic ${num(r.domestic)}, international ${num(r.international)} movements"><td><strong>${safe(r.code)}</strong><small>${state.year===2025&&r.cluster!==undefined?safe(clusters[r.cluster].name):'Airport IATA code'}</small></td><td class="numeric">${num(r.domestic)}</td><td class="numeric">${num(r.international)}</td><td class="numeric"><strong>${num(r.total)}</strong></td></tr>`).join(''):'<tr><td colspan="4">No airports match these filters.</td></tr>';
    $('recordCount').textContent=`Showing ${Math.min(rows.length,state.limit)} of ${rows.length} airports`;$('tableSubtitle').textContent=`${state.year} records · arrivals and departures combined`;$('showMore').disabled=state.limit>=rows.length;$('clusterFilter').disabled=state.year!==2025;renderMap();
  }
  function renderMap(){
    const rows=filtered().filter(r=>Number.isFinite(r.lat)&&Number.isFinite(r.lon)),w=660,h=630,toX=lon=>(lon-67.5)/(98.2-67.5)*w,toY=lat=>(37.7-lat)/(37.7-6.4)*h,max=Math.max(1,...rows.map(r=>r.total));
    const marks=rows.slice().sort((a,b)=>b.total-a.total).map(r=>{const cluster=state.year===2025&&r.cluster!==undefined?r.cluster:null,fill=cluster===null?'#557b98':colors[cluster],radius=Math.min(7,Math.max(3.2,2.8+3.7*Math.sqrt(r.total/max))),label=`${r.code}, ${state.year}: ${num(r.total)} passenger movements`;return `<circle class="airport-marker" role="button" tabindex="0" data-airport="${r.code}" data-tooltip="${safe(label)}; activate to filter" aria-label="Filter to ${safe(label)}" cx="${toX(r.lon).toFixed(2)}" cy="${toY(r.lat).toFixed(2)}" r="${radius.toFixed(2)}" fill="${fill}" fill-opacity=".9" stroke="white"/>`;}).join('');
    $('airportMap').innerHTML=`<svg viewBox="0 0 660 630" role="group" aria-label="Simplified India map with ${rows.length} airport markers"><path d="${window.INDIA_MAP_PATH||''}" fill="#ecf1f5" stroke="#b6c6d2" stroke-width="1.65"/>${marks}<text x="17" y="605" fill="#98a7b4" font-size="11">Geographic illustration · positions approximate</text></svg>`;$('mapCount').textContent=`${rows.length} mapped / ${filtered().length} records`;
    $('airportMap').querySelectorAll('[data-airport]').forEach(n=>{const activate=()=>{state.search=n.dataset.airport;$('airportSearch').value=state.search;state.limit=20;renderTable();$('liveRegion').textContent=`Showing ${state.search} airport.`;};n.addEventListener('click',activate);n.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();activate();}});});
  }
  $('exploreYear').addEventListener('change',e=>{state.year=Number(e.target.value);state.limit=20;state.group='all';$('clusterFilter').value='all';renderTable();});
  $('clusterFilter').addEventListener('change',e=>{state.group=e.target.value;state.limit=20;renderTable();});
  $('airportSearch').addEventListener('input',e=>{state.search=e.target.value.trim().replace(/[^a-z0-9]/gi,'').slice(0,5);state.limit=20;renderTable();});
  $('resetExplorer').addEventListener('click',()=>{Object.assign(state,{year:2025,group:'all',search:'',limit:20});$('exploreYear').value='2025';$('clusterFilter').value='all';$('airportSearch').value='';renderTable();});
  $('showMore').addEventListener('click',()=>{state.limit+=20;renderTable();});
  $('downloadCSV').addEventListener('click',()=>{const rows=filtered(),header='year,airport,domestic_movements,international_movements,total_movements',csv=[header,...rows.map(x=>[x.year,x.code,x.domestic,x.international,x.total].join(','))].join('\r\n'),blob=new Blob(['\uFEFF'+csv],{type:'text/csv;charset=utf-8'}),url=URL.createObjectURL(blob),link=document.createElement('a');link.href=url;link.download=`airconnect_${state.year}_airports.csv`;link.click();URL.revokeObjectURL(url);$('liveRegion').textContent='Airport CSV export started.';});renderTable();

  function bars(target,rows,key,labelKey,tip){const max=Math.max(...rows.map(r=>r[key]));$(target).innerHTML=`<div class="simple-bars">${rows.map((r,i)=>`<div class="simple-bar-row" tabindex="0" data-tooltip="${safe(tip(r))}"><span>${safe(r[labelKey])}</span><div><i style="width:${Math.max(1,r[key]/max*100)}%;background:${colors[i%colors.length]}"></i></div><b>${num(r[key])}</b></div>`).join('')}</div>`;}
  function scatter(target,points,xKey,yKey,aria,tooltip,colorKey=null){
    const w=620,h=300,L=55,R=24,T=18,B=42,xVals=points.map(p=>Math.log10(1+Math.max(0,p[xKey]))),yVals=points.map(p=>Math.log10(1+Math.max(0,p[yKey]))),max=Math.max(...xVals,...yVals),min=Math.min(...xVals,...yVals),sx=v=>L+(v-min)/(max-min||1)*(w-L-R),sy=v=>h-B-(v-min)/(max-min||1)*(h-T-B);
    const marks=points.map((p,i)=>`<circle tabindex="0" cx="${sx(xVals[i]).toFixed(2)}" cy="${sy(yVals[i]).toFixed(2)}" r="3" fill="${colorKey?colors[p[colorKey]%colors.length]:'#17679a'}" fill-opacity=".58" data-tooltip="${safe(tooltip(p))}"/>`).join('');
    $(target).innerHTML=`<svg viewBox="0 0 ${w} ${h}" role="img" aria-label="${safe(aria)}"><line x1="${L}" y1="${h-B}" x2="${w-R}" y2="${T}" stroke="#8b9aaa" stroke-dasharray="5 4"/><line x1="${L}" y1="${h-B}" x2="${w-R}" y2="${h-B}" stroke="#9ba8b4"/><line x1="${L}" y1="${T}" x2="${L}" y2="${h-B}" stroke="#9ba8b4"/>${marks}<text x="${(L+w-R)/2}" y="${h-8}" text-anchor="middle" font-size="11">Actual passenger movements (log scale)</text><text transform="translate(13 ${(T+h-B)/2}) rotate(-90)" text-anchor="middle" font-size="11">Predicted (log scale)</text></svg>`;
  }
  const R=D.regression,rv=Object.fromEntries(R.validation.map(r=>[r.model,r])),rt=Object.fromEntries(R.test.map(r=>[r.model,r])),selectedR=rt[R.selected_model],baseR=rt[R.best_baseline];
  $('regressionMetrics').innerHTML=[metric('Selected ML model',R.selected_model,`${R.feature_count} leakage-safe features`,'Selected by mean validation MAE, not by 2025 test performance.',true),metric('Held-out MAE',num(selectedR.mae),'Passenger movements','Mean absolute error on the untouched 2025 airport-month observations.'),metric('Best baseline MAE',num(baseR.mae),R.best_baseline,'Lowest 2025 MAE among declared naive baselines.'),metric('Test observations',num(R.test_n),'January–December 2025','Every compared method uses the same eligible target rows.')].join('');
  bars('regressionComparison',R.test,'mae','model',r=>`${r.model}: MAE ${num(r.mae)}, RMSE ${num(r.rmse)}, R² ${dec(r.r2,3)}, WAPE ${pct(r.wape)}`);
  scatter('regressionScatter',R.predictions,'actual','selected_prediction',`Actual versus predicted domestic passenger movements for ${R.selected_model}`,p=>`${p.airport} ${p.date}: actual ${num(p.actual)}, predicted ${num(p.selected_prediction)}, residual ${num(p.residual)}`);
  $('regressionRows').innerHTML=R.test.map(r=>`<tr><td><strong>${safe(r.model)}</strong></td><td>${r.type}</td><td class="numeric">${num(rv[r.model]?.mae??0)}</td><td class="numeric">${num(r.mae)}</td><td class="numeric">${num(r.rmse)}</td><td class="numeric">${dec(r.r2,3)}</td><td class="numeric">${pct(r.wape)}</td></tr>`).join('');
  $('regressionFinding').innerHTML=R.beat_best_test_baseline?`<strong>${safe(R.selected_model)} beat the best naive baseline.</strong> Selection was made before the final test evaluation.`:`<strong>The ${safe(R.best_baseline)} remains strongest on 2025 MAE.</strong> ${safe(R.selected_model)} reduced the old annual model error substantially but did not legitimately beat this demanding short-horizon baseline.`;

  const C=D.classification,ct=Object.fromEntries(C.test.map(r=>[r.model,r])),selectedC=ct[C.selected_model];
  $('classificationMetrics').innerHTML=[metric('Selected classifier',C.selected_model,`${C.feature_count} pre-target features`,'Selected by validation balanced accuracy.',true),metric('Balanced accuracy',pct(selectedC.balanced_accuracy),'Held-out 2025','Mean of class-specific recall; robust to class imbalance.'),metric('F1 score',pct(selectedC.f1),'Positive class','Harmonic mean of precision and recall for at least 10% growth.'),metric('ROC-AUC',dec(selectedC.roc_auc,3),`${num(C.test_n)} test records`,'Probability ranking performance; 0.5 is chance.')].join('');
  const cells=[['True negative',selectedC.tn,'Actual 0, predicted 0'],['False positive',selectedC.fp,'Actual 0, predicted 1'],['False negative',selectedC.fn,'Actual 1, predicted 0'],['True positive',selectedC.tp,'Actual 1, predicted 1']];
  $('confusionMatrix').innerHTML=`<div class="matrix-axis top">Predicted class</div><div class="matrix-axis side">Actual class</div><div class="matrix-grid"><span></span><b>0</b><b>1</b><b>0</b>${cells.slice(0,2).map(c=>`<button data-tooltip="${c[0]}: ${c[1]}. ${c[2]}"><strong>${c[1]}</strong><small>${c[0]}</small></button>`).join('')}<b>1</b>${cells.slice(2).map(c=>`<button data-tooltip="${c[0]}: ${c[1]}. ${c[2]}"><strong>${c[1]}</strong><small>${c[0]}</small></button>`).join('')}</div>`;
  const roc=C.roc_curve,w=620,h=300,L=50,Rr=22,T=18,B=42,sx=x=>L+x*(w-L-Rr),sy=y=>h-B-y*(h-T-B),rocPoints=roc.map(p=>`${sx(p.fpr)},${sy(p.tpr)}`).join(' ');
  $('rocChart').innerHTML=`<svg viewBox="0 0 ${w} ${h}" role="img" aria-label="ROC curve with AUC ${selectedC.roc_auc}"><line x1="${L}" y1="${h-B}" x2="${w-Rr}" y2="${T}" stroke="#9aa8b4" stroke-dasharray="5 4"/><polyline points="${rocPoints}" fill="none" stroke="#17679a" stroke-width="3"/><text x="${(L+w-Rr)/2}" y="${h-8}" text-anchor="middle" font-size="11">False positive rate</text><text transform="translate(13 ${(T+h-B)/2}) rotate(-90)" text-anchor="middle" font-size="11">True positive rate</text><text x="${w-Rr-5}" y="${T+18}" text-anchor="end" font-size="12">AUC ${dec(selectedC.roc_auc,3)}</text></svg>`;
  $('classificationRows').innerHTML=C.test.map(r=>`<tr><td><strong>${safe(r.model)}</strong></td><td class="numeric">${pct(r.accuracy)}</td><td class="numeric">${pct(r.balanced_accuracy)}</td><td class="numeric">${pct(r.precision)}</td><td class="numeric">${pct(r.recall)}</td><td class="numeric">${pct(r.f1)}</td><td class="numeric">${r.roc_auc===null?'—':dec(r.roc_auc,3)}</td></tr>`).join('');

  const K=D.clustering,pca=K.pca;
  $('clusterMetrics').innerHTML=[metric('Airports clustered',num(K.n),'Domestic-reporting airports in 2025','Each record has positive domestic passenger traffic.',true),metric('Selected groups',K.k,'Evaluated k = 2–6','Requires at least five airports per cluster and applies a 0.02 silhouette parsimony margin.'),metric('Silhouette',dec(K.silhouette,3),'Higher is better (−1 to 1)','Cohesion and separation in the six-feature scaled space.'),metric('PCA variance',pct(pca.cumulative_explained_variance[1]),'PC1 + PC2','Share of standardised feature variance represented by the two-dimensional projection.')].join('');
  const kw=620,kh=300,kL=55,kR=40,kT=20,kB=42,kMax=Math.max(...K.evaluations.map(r=>r.inertia)),ksx=k=>kL+(k-2)/4*(kw-kL-kR),ksyS=s=>kh-kB-(s-.35)/.2*(kh-kT-kB),ksyI=i=>kh-kB-i/kMax*(kh-kT-kB);
  $('clusterSelection').innerHTML=`<svg viewBox="0 0 ${kw} ${kh}" role="img" aria-label="K-Means inertia and silhouette scores for k two through six"><polyline points="${K.evaluations.map(r=>`${ksx(r.k)},${ksyS(r.silhouette)}`).join(' ')}" fill="none" stroke="#17679a" stroke-width="3"/><polyline points="${K.evaluations.map(r=>`${ksx(r.k)},${ksyI(r.inertia)}`).join(' ')}" fill="none" stroke="#6f858e" stroke-width="2"/>${K.evaluations.map(r=>`<circle tabindex="0" cx="${ksx(r.k)}" cy="${ksyS(r.silhouette)}" r="5" fill="#17679a" data-tooltip="k=${r.k}: silhouette ${dec(r.silhouette,3)}, inertia ${dec(r.inertia,1)}, minimum group ${r.minimum_cluster_size}"/>`).join('')}<text x="${kw/2}" y="${kh-8}" text-anchor="middle" font-size="11">Number of clusters k</text></svg>`;
  const pcs=pca.points,pw=620,ph=300,pL=45,pR=20,pT=18,pB=38,xmin=Math.min(...pcs.map(p=>p.pc1)),xmax=Math.max(...pcs.map(p=>p.pc1)),ymin=Math.min(...pcs.map(p=>p.pc2)),ymax=Math.max(...pcs.map(p=>p.pc2)),px=x=>pL+(x-xmin)/(xmax-xmin)*(pw-pL-pR),py=y=>ph-pB-(y-ymin)/(ymax-ymin)*(ph-pT-pB);
  $('pcaChart').innerHTML=`<svg viewBox="0 0 ${pw} ${ph}" role="img" aria-label="PCA projection of 2025 airport features coloured by K-Means cluster">${pcs.map(p=>`<circle tabindex="0" cx="${px(p.pc1)}" cy="${py(p.pc2)}" r="4" fill="${colors[p.cluster]}" fill-opacity=".75" data-tooltip="${p.airport}: PC1 ${dec(p.pc1,2)}, PC2 ${dec(p.pc2,2)}, cluster ${K.clusters[p.cluster].name}"/>`).join('')}<text x="${pw/2}" y="${ph-7}" text-anchor="middle" font-size="11">Principal component 1</text><text transform="translate(12 ${ph/2}) rotate(-90)" text-anchor="middle" font-size="11">Principal component 2</text></svg>`;
  $('clusterBars').innerHTML=K.clusters.map(c=>`<div class="cluster-row" tabindex="0" data-tooltip="${safe(c.name)}: ${c.count} airports"><div class="cluster-caption"><strong>${safe(c.name)}</strong><span>${c.count} airports</span></div><div class="bar-track"><div class="bar-fill" style="width:${c.count/K.n*100}%;background:${colors[c.id]}"></div></div></div>`).join('');
  $('clusterDetails').innerHTML=K.clusters.map(c=>`<div class="cluster-detail"><h3><i class="dot" style="background:${colors[c.id]}"></i>${safe(c.name)}</h3><p>Median domestic: <strong>${num(c.median_domestic)}</strong></p><p>Median international: <strong>${num(c.median_international)}</strong></p><p>Median growth: <strong>${pct(c.median_growth)}</strong></p><p>Examples: ${c.examples.map(safe).join(' · ')}</p></div>`).join('');

  document.querySelectorAll('[data-ml-tab]').forEach(tab=>tab.addEventListener('click',()=>{document.querySelectorAll('[data-ml-tab]').forEach(t=>{const active=t===tab;t.classList.toggle('active',active);t.setAttribute('aria-selected',String(active));});document.querySelectorAll('.ml-view').forEach(view=>view.hidden=view.id!==`ml-${tab.dataset.mlTab}`);$('liveRegion').textContent=`Showing ${tab.textContent} machine learning results.`;}));

  // Upgrade native title hints to a viewport-aware tooltip for mouse, keyboard and touch.
  document.querySelectorAll('[title]').forEach(el=>{if(!el.dataset.tooltip)el.dataset.tooltip=el.getAttribute('title');el.removeAttribute('title');});
  const tip=$('tooltip');let tipTarget=null;
  function showTip(target,x,y){const text=target?.dataset?.tooltip;if(!text)return;tipTarget=target;tip.textContent=text;tip.hidden=false;const box=tip.getBoundingClientRect(),left=Math.max(8,Math.min((x??target.getBoundingClientRect().left)-box.width/2,window.innerWidth-box.width-8)),top=Math.max(8,Math.min((y??target.getBoundingClientRect().bottom+8),window.innerHeight-box.height-8));tip.style.left=`${left}px`;tip.style.top=`${top}px`;target.setAttribute('aria-describedby','tooltip');}
  function hideTip(){if(tipTarget)tipTarget.removeAttribute('aria-describedby');tipTarget=null;tip.hidden=true;}
  document.addEventListener('mouseover',e=>{const t=e.target.closest('[data-tooltip]');if(t)showTip(t,e.clientX,e.clientY+15);});document.addEventListener('mouseout',e=>{if(e.target.closest('[data-tooltip]'))hideTip();});document.addEventListener('focusin',e=>{const t=e.target.closest('[data-tooltip]');if(t)showTip(t);});document.addEventListener('focusout',hideTip);document.addEventListener('pointerdown',e=>{const t=e.target.closest('[data-tooltip]');if(t&&e.pointerType==='touch')showTip(t,e.clientX,e.clientY+15);});document.addEventListener('keydown',e=>{if(e.key==='Escape')hideTip();});
})();
