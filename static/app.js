// ===========================
// TiHive SmartOps – app.js
// ===========================

// ---------- helpers ----------
const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => Array.from(document.querySelectorAll(sel));
const $el = (tag, cls) => { const e=document.createElement(tag); if(cls) e.className=cls; return e; };
const nowStr = () => new Date().toLocaleString();

// ---------- parsing (depuis rapports TEXTE) ----------
function parseQuality(report){
  if(!report) return {score:null, nonCompliantBatches:0, note:"aucun rapport"};
  const nonc = (report.match(/Non[- ]?compliant|non[- ]?conform/gi)||[]).length;
  const totalBatches = (report.match(/Batch\s+\d+/g)||[]).length || 0;
  const score = totalBatches ? Math.max(0, Math.round(100 - (nonc/totalBatches)*100)) : null;
  return {score, nonCompliantBatches:nonc, note: totalBatches? `${totalBatches} lots` : "—"};
}
function parseEco(report){
  if(!report) return {score:null, note:"aucun rapport"};
  const full = /full compliance|pleine conformité/i.test(report);
  const devi = (report.match(/exceeded|deviation|hotspot|dépassement|écart/gi)||[]).length;
  let score = full ? 95 : Math.max(40, 95 - devi*8);
  score = Math.min(100, Math.max(0, Math.round(score)));
  return {score, note: full ? "pleine conformité" : `${devi} écarts`};
}
function parseMaintenance(report){
  if(!report) return {alerts:null, note:"aucun rapport"};
  const crit = (report.match(/critical|priorit[y|é]\s*haute|High priority/gi)||[]).length;
  const warn = (report.match(/warn|overheat|drift|overheating|avertissement/gi)||[]).length;
  return {alerts: crit + Math.min(1, warn), note: `${crit} critiques / ${warn} avert.`};
}
function parseProcess(report){
  if(!report) return {score:null, note:"aucun rapport"};
  const issues = (report.match(/deviation|out[- ]of[- ]spec|instability|écart|instabilité/gi)||[]).length;
  let score = Math.max(40, 95 - issues*7);
  score = Math.min(100, Math.max(0, Math.round(score)));
  return {score, note: `${issues} problèmes`};
}

// ---------- KPIs globaux ----------
function updateKPIs(kind, parsed){
  switch(kind){
    case "quality":
      if(parsed.score!=null) $("#kpiQualityScore").textContent = parsed.score + "/100";
      $("#kpiQualityNote").textContent = parsed.note;
      break;
    case "process":
      if(parsed.score!=null) $("#kpiProcessScore").textContent = parsed.score + "/100";
      $("#kpiProcessNote").textContent = parsed.note;
      break;
    case "maintenance":
      if(parsed.alerts!=null) $("#kpiMaintAlerts").textContent = parsed.alerts;
      $("#kpiMaintNote").textContent = parsed.note;
      break;
    case "eco":
      if(parsed.score!=null) $("#kpiEcoScore").textContent = parsed.score + "/100";
      $("#kpiEcoNote").textContent = parsed.note;
      break;
  }
}

// ---------- Snapshots ----------
function addSnapshot(kind, parsed){
  const list = $("#snapshotList");
  const item = $el("div","item");
  const left = $el("div");
  left.innerHTML = `<b>${kind.toUpperCase()}</b><br/><small>${nowStr()}</small>`;
  const pill = $el("span","pill");
  let label="OK", cls="ok";
  if(kind==="maintenance"){
    label = (parsed.alerts||0)>0 ? `${parsed.alerts} alertes` : "0 alerte";
    cls = (parsed.alerts||0)>0 ? "bad" : "ok";
  } else {
    const v = parsed.score==null?"–":parsed.score;
    label = v==="–" ? "–" : `${v}/100`;
    cls = parsed.score!=null && parsed.score<70 ? "bad" : "ok";
  }
  pill.textContent = label; pill.classList.add(cls);
  item.append(left,pill);
  list.prepend(item);
}

// ---------- Historique ----------
const historyState = [];
function pushHistory(kind, report){
  historyState.unshift({kind, ts:Date.now(), report});
  renderHistory();
}
function renderHistory(){
  const root = $("#historyList");
  root.innerHTML = "";
  for(const item of historyState){
    const div = $el("div","entry");
    const h = $el("div");
    h.innerHTML = `<b>${item.kind.toUpperCase()}</b> — <small>${new Date(item.ts).toLocaleString()}</small>`;
    const pre = $el("pre","output");
    pre.textContent = item.report;
    div.append(h,pre);
    root.appendChild(div);
  }
}

// ---------- Tables & Charts ----------
function renderTables(rootId, tables){
  const root = document.getElementById(rootId);
  root.innerHTML = "";
  if(!tables || !tables.length) return;
  for(const t of tables){
    const wrap = $el("div");
    const h = $el("h4"); h.textContent = t.title || "Table"; wrap.appendChild(h);
    const table = $el("table","table");
    const thead = $el("thead"); const trh = $el("tr");
    (t.columns||[]).forEach(c=>{ const th=$el("th"); th.textContent=c; trh.appendChild(th); });
    thead.appendChild(trh); table.appendChild(thead);
    const tbody = $el("tbody");
    (t.rows||[]).forEach(r=>{
      const tr=$el("tr");
      r.forEach(v=>{ const td=$el("td"); td.textContent = v; tr.appendChild(td); });
      tbody.appendChild(tr);
    });
    table.appendChild(tbody); wrap.appendChild(table); root.appendChild(wrap);
  }
}

const _chartRefs = {};
function renderCharts(rootId, charts){
  const root = document.getElementById(rootId);
  // destroy previous charts if any
  if(_chartRefs[rootId]){
    for(const ch of _chartRefs[rootId]) try{ ch.destroy(); }catch(e){}
  }
  _chartRefs[rootId] = [];
  root.innerHTML = "";
  if(!charts || !charts.length) return;

  for(const c of charts){
    const card = $el("div","chart-card");
    const title = $el("h4"); title.textContent = c.title || "Chart"; card.appendChild(title);
    const canvas = $el("canvas"); card.appendChild(canvas);
    root.appendChild(card);
    const cfg = {
      type: c.type || "bar",
      data: {
        labels: c.labels || [],
        datasets: (c.datasets||[]).map(ds=>({
          label: ds.label || "",
          data: ds.data || [],
          fill: false,
          tension: 0.25 // lissage line
        }))
      },
      options: {
        responsive: true,
        plugins: { legend: { display: true } },
        scales: { x: { grid: { display:false }}, y: { beginAtZero:true } }
      }
    };
    const chart = new Chart(canvas.getContext("2d"), cfg);
    _chartRefs[rootId].push(chart);
  }
}

// ---------- Navigation ----------
function activatePanel(id){
  $$(".panel").forEach(p=>p.classList.remove("active"));
  $$(".nav a").forEach(a=>a.classList.remove("active"));
  const panel = document.getElementById(id);
  if(panel){ panel.classList.add("active"); }
  const link = document.querySelector(`.nav a[href="#${id}"]`);
  if(link){ link.classList.add("active"); }
  $("#sectionTitle").textContent = ({
    overview:"Aperçu", quality:"Qualité", process:"Procédé", maintenance:"Maintenance", eco:"Environnement", history:"Historique"
  }[id] || id.charAt(0).toUpperCase()+id.slice(1));
}

// ---------- Thème ----------
function toggleTheme(){
  document.body.classList.toggle("light");
  localStorage.setItem("theme", document.body.classList.contains("light") ? "light":"dark");
}

// ---------- DnD pour inputs fichier ----------
function setupDragAndDrop(){
  $$(".file").forEach(lbl=>{
    const input = lbl.querySelector("input[type=file]");
    const span = lbl.querySelector("span");
    lbl.addEventListener("dragover", (e)=>{ e.preventDefault(); lbl.style.borderColor="#6aa3ff"; });
    lbl.addEventListener("dragleave", ()=>{ lbl.style.borderColor="var(--border)"; });
    lbl.addEventListener("drop", (e)=>{
      e.preventDefault(); lbl.style.borderColor="var(--border)";
      if(e.dataTransfer.files && e.dataTransfer.files[0]){
        input.files = e.dataTransfer.files;
        span.textContent = e.dataTransfer.files[0].name;
      }
    });
    input.addEventListener("change", ()=>{
      span.textContent = input.files && input.files[0] ? input.files[0].name : span.dataset.placeholder || "Choisir un fichier ou déposer ici";
    });
  });
}

// ---------- Appel API agents ----------
async function callAgent(agent, form, outId, statusId, kpiContainer){
  const out = $(outId);
  const status = $(statusId);
  status.textContent = "running…"; status.classList.add("busy");
  out.textContent = "⏳ Exécution...";
  const body = new FormData(form);
  try{
    const res = await fetch(`/api/run/${agent}`, {method:"POST", body});
    const data = await res.json();
    if(!data.ok) throw new Error(data.error || "Erreur inconnue");
    const report = (data.report || "").trim();
    out.textContent = report || "(rapport vide)";

    // KPIs par agent
    let parsed;
    if(agent==="quality") parsed = parseQuality(report);
    if(agent==="process") parsed = parseProcess(report);
    if(agent==="maintenance") parsed = parseMaintenance(report);
    if(agent==="eco") parsed = parseEco(report);
    updateKPIs(agent, parsed);
    addSnapshot(agent, parsed);

    // mini-kpis (pills)
    if(kpiContainer){
      kpiContainer.innerHTML = "";
      const pills = [];
      if(agent==="maintenance"){ pills.push(`${parsed.alerts??"–"} alertes`, parsed.note); }
      else { pills.push(`${parsed.score??"–"}/100`, parsed.note); }
      for(const p of pills){ const span = $el("span","pill"); span.textContent = p; kpiContainer.appendChild(span); }
    }

    // visualisations (tables + charts)
    if(data.viz){
      renderTables(`tbl-${agent}`, data.viz.tables);
      renderCharts(`chr-${agent}`, data.viz.charts);
    } else {
      // clear previous viz if no viz returned
      renderTables(`tbl-${agent}`, []);
      renderCharts(`chr-${agent}`, []);
    }

    status.textContent = "done"; status.classList.remove("busy"); status.classList.add("ok");
    pushHistory(agent, report);
  }catch(e){
    out.textContent = "❌ " + e.message;
    status.textContent = "error"; status.classList.remove("busy"); status.classList.add("err");
  }
}

// ---------- Run all (séquentiel, évite 429) ----------
async function runAll(){
  $("#outAll").textContent = "Démarrage de l'exécution séquentielle…";
  const seq = [
    ()=>callAgent("quality", $("#form-quality"), "#out-quality", "#statusQuality", $("#qualityKPIs")),
    ()=>callAgent("process", $("#form-process"), "#out-process", "#statusProcess", $("#processKPIs")),
    ()=>callAgent("maintenance", $("#form-maintenance"), "#out-maintenance", "#statusMaint", $("#maintKPIs")),
    ()=>callAgent("eco", $("#form-eco"), "#out-eco", "#statusEco", $("#ecoKPIs")),
  ];
  for(const step of seq){ await step(); }
  $("#outAll").textContent += "\nTerminé.";
}

// ---------- Init ----------
window.addEventListener("DOMContentLoaded", ()=>{
  // Navigation
  $$(".nav a").forEach(a=>{
    a.addEventListener("click",(e)=>{ e.preventDefault(); activatePanel(a.getAttribute("href").slice(1)); });
  });
  activatePanel("overview");

  // Thème
  if(localStorage.getItem("theme")==="light") document.body.classList.add("light");
  $("#themeToggle").addEventListener("click", toggleTheme);

  // Forms → callAgent
  const map = [
    { id:"form-quality", out:"#out-quality", status:"#statusQuality", kpi:"#qualityKPIs", kind:"quality" },
    { id:"form-process", out:"#out-process", status:"#statusProcess", kpi:"#processKPIs", kind:"process" },
    { id:"form-maintenance", out:"#out-maintenance", status:"#statusMaint", kpi:"#maintKPIs", kind:"maintenance" },
    { id:"form-eco", out:"#out-eco", status:"#statusEco", kpi:"#ecoKPIs", kind:"eco" },
  ];
  for (const m of map){
    const form = document.getElementById(m.id);
    form.addEventListener("submit",(e)=>{
      e.preventDefault();
      callAgent(m.kind, form, m.out, m.status, document.querySelector(m.kpi));
    });
  }

  // DnD
  setupDragAndDrop();

  // Run all
  $("#btnRunAll").addEventListener("click", runAll);
});
