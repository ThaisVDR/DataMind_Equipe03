'use strict';
(() => {
  const D = window.DATAMIND;
  const $ = id => document.getElementById(id);
  if (!D || !D.meta) { $('load-error').hidden = false; return; }
  const n = (v, decimals = 0) => v == null ? '—' : Number(v).toLocaleString('pt-BR', {minimumFractionDigits: decimals, maximumFractionDigits: decimals});
  const pct = v => v == null ? '—' : `${n(v, 2)}%`;
  const esc = v => String(v ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const color = {tca:'#28664f',tda:'#bd674d',tap:'#c3a153'};
  function table(id, headers, rows) {
    $(id).innerHTML = `<table><thead><tr>${headers.map(h => `<th scope="col">${esc(h)}</th>`).join('')}</tr></thead><tbody>${rows.map(row=>`<tr>${row.map(v=>`<td>${esc(v)}</td>`).join('')}</tr>`).join('')}</tbody></table>`;
  }
  function metrics(id, list) { $(id).innerHTML = list.map(([value,label])=>`<div class="metric"><strong>${esc(value)}</strong><span>${esc(label)}</span></div>`).join(''); }
  function lineChart(id, years, series, maximum=100) {
    const W=880,H=258,L=45,R=25,T=18,B=38;
    const x=i=>L+i*(W-L-R)/Math.max(1,years.length-1), y=v=>T+(maximum-v)/maximum*(H-T-B);
    let svg=`<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(series.map(s=>s.name).join(', '))}. Valores completos disponíveis na tabela.">`;
    for(let i=0;i<=4;i++){const v=i*maximum/4;svg+=`<line class="grid" x1="${L}" x2="${W-R}" y1="${y(v)}" y2="${y(v)}"/><text x="${L-9}" y="${y(v)+4}" text-anchor="end">${n(v)}%</text>`;}
    years.forEach((year,i)=>{svg+=`<text x="${x(i)}" y="${H-10}" text-anchor="middle">${esc(year)}</text>`;});
    for(const s of series){let path='';s.values.forEach((v,i)=>{if(v==null){path+=' ';return;}path+=`${i===0||s.values[i-1]==null?'M':'L'}${x(i)},${y(v)} `;});svg+=`<path class="line" stroke="${s.color}" d="${path}"/>`;s.values.forEach((v,i)=>{if(v!=null)svg+=`<circle class="point" cx="${x(i)}" cy="${y(v)}" r="4" fill="${s.color}"><title>${esc(s.name)} · ${years[i]}: ${pct(v)}</title></circle>`;});}
    $(id).innerHTML=svg+'</svg>';
  }
  const bar = (value, cls) => value == null ? '<span class="muted">Sem grupo elegível</span>' : `<div class="bar-track"><div class="bar-fill ${cls}" style="width:${Math.max(0,Math.min(100,Number(value)))}%"></div><span class="bar-value">${pct(value)}</span></div>`;
  function p1(){
    const cohort=Number($('coorte').value),rows=D.p1.filter(r=>r.coorte===cohort),last=rows.at(-1),peak=rows.reduce((a,b)=>a.tada>b.tada?a:b);
    $('coorte-context').textContent=`${n(last.n)} ingressantes · ${last.cursos} cursos · ${2024-cohort+1} anos de acompanhamento`;
    $('outcome-stats').innerHTML=[[last.tca,'chegam ao diploma'],[last.tda,'desistem do curso'],[last.tap,'ainda permanecem']].map(([v,t])=>`<div><strong>${n(v,1)}</strong><span>${t}</span></div>`).join('');
    // Maior resto: exatamente 100 pontos e arredondamento consistente.
    const rates=[last.tca,last.tda,last.tap],counts=rates.map(Math.floor);let remaining=100-counts.reduce((a,b)=>a+b,0);
    const order=rates.map((r,i)=>({i,frac:r-counts[i]})).sort((a,b)=>b.frac-a.frac);for(let j=0;j<remaining;j++)counts[order[j%3].i]++;
    $('waffle').innerHTML=counts.map((count,i)=>Array.from({length:count},()=>`<i class="${['green','coral','gold'][i]}"></i>`).join('')).join('');
    $('peak-title').textContent=`A maior perda acontece no ${peak.referencia-cohort+1}º ano.`;
    $('peak-text').textContent=`Em ${peak.referencia}, a desistência anual correspondeu a ${pct(peak.tada)} da base efetiva da coorte. Esse é o maior incremento anual observado nesta turma.`;
    lineChart('trajectory-chart',rows.map(r=>r.referencia),['tca','tda','tap'].map(k=>({name:{tca:'Conclusão',tda:'Desistência',tap:'Permanência'}[k],color:color[k],values:rows.map(r=>r[k])})));
    table('trajectory-table',['Ano','Ano do curso','Base efetiva','Conclusão','Desistência','Permanência','Desistência no ano'],rows.map(r=>[r.referencia,r.referencia-cohort+1,n(r.denominador),pct(r.tca),pct(r.tda),pct(r.tap),pct(r.tada)]));
  }
  function p2(){
    const cohort=Number($('compare-coorte').value),level=$('level').value,dir=$('order').value==='asc'?1:-1;
    const rows=D.p2[level].filter(r=>r.coorte===cohort).sort((a,b)=>dir===1?a.tda-b.tda:b.tda-a.tda);const base=new Map(D.p2[level].filter(r=>r.coorte===2015).map(r=>[r[level],r]));
    $('comparison-label').textContent=cohort;
    $('ranking').innerHTML=rows.slice(0,12).map(r=>`<div class="bar-row"><div class="bar-name">${esc(r[level])}<small>${r.cursos} cursos · base ${n(r.denominador)}</small></div><div>${bar(base.get(r[level])?.tda,'gray')}${bar(r.tda,'green')}</div></div>`).join('');
    table('ranking-table',[level==='area'?'Área':'Rótulo CINE','2015 · TDA',`${cohort} · TDA`,'Variação (p.p.)','Base efetiva comparada'],rows.map(r=>{const b=base.get(r[level]);return[r[level],pct(b?.tda),pct(r.tda),b?n(r.tda-b.tda,2):'Sem correspondência',n(r.denominador)];}));
  }
  const networkNames=['Pública','Privada com fins lucrativos','Privada sem fins lucrativos'];
  const networkColors=['#28664f','#bd674d','#5d8198'];
  function p3(){
    const modality=$('modality').value,year=Number($('census-year').value),rows=D.p3.filter(r=>r.modalidade===modality);
    lineChart('network-chart',[2021,2022,2023,2024],networkNames.map((name,i)=>({name,color:networkColors[i],values:[2021,2022,2023,2024].map(y=>rows.find(r=>r.ano===y&&r.rede===name)?.proxy)})),50);
    $('network-legend').innerHTML=networkNames.map((name,i)=>`<span><i style="background:${networkColors[i]}"></i>${esc(name)}</span>`).join('');
    const subset=rows.filter(r=>r.ano===year),total=subset.reduce((s,r)=>s+r.matriculas,0);
    $('enrollment-caption').textContent=`${year} · ${n(total)} matrículas nas redes exibidas`;
    $('enrollment').innerHTML=subset.map(r=>`<div class="bar-row"><div class="bar-name">${esc(r.rede)}<small>${n(r.matriculas)} matrículas</small></div>${bar(100*r.matriculas/total,'green')}</div>`).join('');
    const pub=y=>rows.find(r=>r.ano===y&&r.rede==='Pública');
    $('anomaly').textContent=`Na rede pública ${modality==='1'?'presencial':'EAD'}, a proxy passou de ${pct(pub(2022)?.proxy)} em 2022 para ${pct(pub(2023)?.proxy)} em 2023, voltando a ${pct(pub(2024)?.proxy)} em 2024. O padrão exige investigação; a causa ainda não está demonstrada.`;
    table('network-table',['Ano','Rede','Matrículas','Base da proxy','Evasão anual'],rows.map(r=>[r.ano,r.rede,n(r.matriculas),n(r.n),pct(r.proxy)]));
  }
  function p4(){
    const j=D.qualidade.juncoes.find(r=>r.pergunta==='P4');metrics('cpc-stats',[[`${j.correspondentes} / ${j.origem}`,'cursos com correspondência na trajetória'],[n(j.elegiveis),'cursos elegíveis para a análise'],[n(D.correlacao_cpc.pearson,3),'Pearson por curso · sem ajustes']]);
    $('cpc-bars').innerHTML=D.p4.map(r=>`<div class="bar-row"><div class="bar-name">CPC faixa ${esc(r.faixa)}<small>${r.cursos} cursos · base ${n(r.denominador)}</small></div>${bar(r.tda,'coral')}</div>`).join('');
    table('cpc-table',['Faixa CPC','Cursos','Base efetiva','Desistência','Conclusão'],D.p4.map(r=>[r.faixa,r.cursos,n(r.denominador),pct(r.tda),pct(r.tca)]));
  }
  function p5(){
    const j=D.qualidade.juncoes.find(r=>r.pergunta==='P5');metrics('lic-stats',[[`${j.correspondentes} / ${j.origem}`,'licenciaturas com correspondência'],[n(j.elegiveis),'cursos elegíveis após os filtros'],[n(D.p5.reduce((s,r)=>s+r.participantes,0)),'participantes do Enade nos cursos elegíveis']]);
    const rows=[...D.p5].sort((a,b)=>a.tca-b.tca);
    $('lic-bars').innerHTML=rows.map(r=>`<div class="bar-row"><div class="bar-name">${esc(r.area_enade)}<small>${r.cursos} cursos elegíveis</small></div><div>${bar(r.tca,'green')}${bar(r.proficiencia,'blue')}</div></div>`).join('');
    table('lic-table',['Área','Base trajetória','Desistência','Conclusão','Participantes 2025','Proficiência'],rows.map(r=>[r.area_enade,n(r.denominador),pct(r.tda),pct(r.tca),n(r.participantes),pct(r.proficiencia)]));
  }
  function eda(){
    metrics('eda-stats',[[D.meta.fontes,'conjuntos ativos no PostgreSQL'],[n(D.meta.linhas),'registros em granularidades diferentes'],['≥ 10','base mínima dos grupos publicados']]);
    table('profile-table',['Fonte','Período','Linhas','Cursos distintos','Ausências verificadas','Sequenciais excluídos'],D.qualidade.perfis.map(r=>[r.fonte,r.periodo,n(r.linhas),n(r.cursos),n(r.campos_ausentes),n(r.excluidos_sequenciais)]));
    table('joins-table',['Pergunta','Origem','Match','Taxa','Elegíveis'],D.qualidade.juncoes.map(r=>[r.pergunta,r.origem,r.correspondentes,pct(r.taxa_match),r.elegiveis]));
    table('indicator-table',['Indicador','Ano','Registros','Métrica','Ausentes'],D.qualidade.indicadores.map(r=>[r.tipo,r.ano,r.linhas,r.metrica,r.ausentes]));
    table('ibge-table',['Tabela SIDRA','Estado original','Registros preservados'],D.qualidade.ibge.map(r=>[r.tabela,r.status_valor,n(r.linhas)]));
    $('checks').innerHTML=D.qualidade.verificacoes.map(v=>`<li>${esc(v)}</li>`).join('');
    table('sources-table',['Conjunto','Família','Arquivo local','Linhas','SHA-256 (início)'],D.fontes.map(r=>[r.source_key,r.family,r.source_path.split('/').at(-1),n(r.rows_loaded),r.sha256.slice(0,16)]));
  }
  function route(){
    const id=location.hash.slice(1),valid=['trajetoria','cursos','redes','qualidade','licenciaturas','evidencias'],active=valid.includes(id)?id:'trajetoria';
    document.querySelectorAll('.page').forEach(e=>e.hidden=e.id!==active);
    document.querySelectorAll('nav a').forEach(a=>{a.classList.toggle('active',a.dataset.tab===active);if(a.dataset.tab===active)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current');});
    document.title=`${{trajetoria:'A rota da turma',cursos:'Cursos e áreas',redes:'Redes e modalidades',qualidade:'Qualidade e retenção',licenciaturas:'Licenciaturas',evidencias:'Evidências e método'}[active]} · Rota do Diploma`;
    window.scrollTo(0,0);
  }
  $('coorte').innerHTML=[2015,2016,2017,2018,2019,2020].map(y=>`<option>${y}</option>`).join('');
  $('compare-coorte').innerHTML=[2020,2019,2018,2017,2016].map(y=>`<option>${y}</option>`).join('');
  $('coorte').addEventListener('change',p1);['compare-coorte','level','order'].forEach(id=>$(id).addEventListener('change',p2));['modality','census-year'].forEach(id=>$(id).addEventListener('change',p3));
  $('download').addEventListener('click',()=>{const url=URL.createObjectURL(new Blob([JSON.stringify(D,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='datamind-snapshot.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
  $('snapshot-time').textContent=`Extração: ${new Date(D.meta.gerado_em).toLocaleString('pt-BR',{timeZone:'America/Cuiaba'})} · Cuiabá`;
  document.querySelectorAll('a[href^="#"]').forEach(link=>link.addEventListener('click',event=>{
    const destination=link.getAttribute('href').slice(1);
    if(destination==='main'){event.preventDefault();$('main').scrollIntoView({behavior:'smooth'});return;}
    if(['trajetoria','cursos','redes','qualidade','licenciaturas','evidencias'].includes(destination)){
      event.preventDefault();history.pushState(null,'',`#${destination}`);route();
    }
  }));
  window.addEventListener('popstate',route);p1();p2();p3();p4();p5();eda();route();
})();
