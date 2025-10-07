from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv

# ====== Agents ======
from Agents.TiHiveSmartOps import (
    create_quality_reasoner_agent,
    create_process_advisor_agent,
    create_maintenance_advisor_agent,
    create_eco_insight_agent,
)

# ====== Libs pour viz/fallback ======
import pandas as pd
import yaml

# -----------------------
#  Config & chemins
# -----------------------
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent  # racine du projet
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
UPLOAD_DIR = BASE_DIR / "uploads"
KB_DIR = BASE_DIR / "kb"
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

for p in (UPLOAD_DIR, KB_DIR, DATA_DIR, LOGS_DIR):
    p.mkdir(parents=True, exist_ok=True)

app = Flask(__name__, template_folder=str(TEMPLATES_DIR), static_folder=str(STATIC_DIR))


# -----------------------
#  Utils génériques
# -----------------------
def _to_abs(p: str | Path) -> str:
    return str(Path(p).resolve())

def _extract_text(res: Any) -> str:
    """
    Agno peut renvoyer un objet (RunOutput) ou une str.
    On priorise .content puis .output_text, sinon str(res).
    """
    if isinstance(res, str):
        return res
    # Certains wrappers ont .content
    txt = getattr(res, "content", None)
    if isinstance(txt, str) and txt.strip():
        return txt
    # Parfois .output_text
    txt = getattr(res, "output_text", None)
    if isinstance(txt, str) and txt.strip():
        return txt
    # Parfois messages[-1].content
    try:
        messages = getattr(res, "messages", None)
        if isinstance(messages, list) and messages:
            last = messages[-1]
            txt = getattr(last, "content", None)
            if isinstance(txt, str) and txt.strip():
                return txt
    except Exception:
        pass
    return str(res or "").strip()

def _parse_analyze_prompt(prompt: str) -> tuple[Optional[str], Optional[str]]:
    """
    Extrait 'Analyze <src> using <rules>' depuis le prompt.
    """
    m = re.search(r"Analyze\s+(.+?)\s+using\s+(.+)", prompt, flags=re.I)
    if not m:
        return None, None
    src = m.group(1).strip().strip("'\"")
    rules = m.group(2).strip().strip("'\"")
    return src, rules


# -----------------------
#  Fallback Quality local
# -----------------------
def _fallback_quality_report(csv_path: str, yaml_path: str) -> str:
    df = pd.read_csv(csv_path)
    with open(yaml_path, "r", encoding="utf-8") as f:
        rules = yaml.safe_load(f) or {}

    h = rules.get("humidity", {})
    d = rules.get("density", {})
    t = rules.get("thickness", {})

    hum_min, hum_max = h.get("min"), h.get("max")
    den_min, den_max = d.get("min"), d.get("max")
    th_min, th_max = t.get("min"), t.get("max")

    deviations: List[tuple[Any, str, str]] = []
    batches: List[str] = []

    for idx, row in df.iterrows():
        bid = row.get("batch_id", idx)
        batches.append(str(int(bid)) if pd.notna(bid) else str(idx))

        # Humidity
        hv = row.get("humidity", None)
        if pd.notna(hv):
            if hum_min is not None and hv < hum_min:
                deviations.append((bid, "Humidity", f"{hv}% (−{hum_min-hv:.2f}% below {hum_min}%)"))
            elif hum_max is not None and hv > hum_max:
                deviations.append((bid, "Humidity", f"{hv}% (+{hv-hum_max:.2f}% above {hum_max}%)"))

        # Density
        dv = row.get("density", None)
        if pd.notna(dv):
            if den_min is not None and dv < den_min:
                deviations.append((bid, "Density", f"{dv} g/cm³ (−{den_min-dv:.3f} below {den_min})"))
            elif den_max is not None and dv > den_max:
                deviations.append((bid, "Density", f"{dv} g/cm³ (+{dv-den_max:.3f} above {den_max})"))

        # Thickness
        tv = row.get("thickness", None)
        if pd.notna(tv):
            if th_min is not None and tv < th_min:
                deviations.append((bid, "Thickness", f"{tv} mm (−{th_min-tv:.2f} below {th_min})"))
            elif th_max is not None and tv > th_max:
                deviations.append((bid, "Thickness", f"{tv} mm (+{tv-th_max:.2f} above {th_max})"))

    lines = []
    lines.append("=== Quality Diagnostic Report ===")
    lines.append("📘 Context:")
    lines.append(f"Analyzed file: {csv_path}")
    lines.append(f"Rules: {yaml_path}")
    lines.append("")
    lines.append("📊 Summary:")
    uniq = ", ".join(batches) if batches else "—"
    lines.append(f"Batches analyzed: {uniq}")
    if not deviations:
        lines.append("")
        lines.append("✅ Overall Assessment:")
        lines.append("All batches: Compliant")
        lines.append("--- END OF REPORT ---")
        return "\n".join(lines)

    lines.append("")
    lines.append("⚠️ Detected Deviations:")
    for bid, k, desc in deviations:
        lines.append(f"- Batch {bid}: {k} → {desc}")

    lines.append("")
    lines.append("💡 Analysis & Interpretation:")
    lines.append("Observed deviations suggest process drift or sensor calibration issues on affected batches.")
    lines.append("")
    lines.append("🧭 Corrective and Preventive Recommendations:")
    lines.append("- Verify drying parameters and compression tooling; calibrate sensors.")
    lines.append("- Add in-process SPC for humidity & thickness.")
    lines.append("")
    lines.append("📈 Observations / Trends:")
    lines.append("Monitor next batches to confirm if deviations persist.")
    lines.append("")
    lines.append("✅ Overall Assessment:")
    lines.append("Mixed compliance. Non-conforming batches listed above.")
    lines.append("--- END OF REPORT ---")
    return "\n".join(lines)


# -----------------------
#  Génération des viz
# -----------------------
def _build_quality_viz(csv_path: str, yaml_path: str) -> Dict[str, Any]:
    df = pd.read_csv(csv_path)
    with open(yaml_path, "r", encoding="utf-8") as f:
        rules = yaml.safe_load(f) or {}
    hum = rules.get("humidity", {}); den = rules.get("density", {}); th = rules.get("thickness", {})

    rows = []
    for idx, r in df.iterrows():
        bid = int(r.get("batch_id", idx))
        h = float(r.get("humidity", float("nan")))
        d = float(r.get("density", float("nan")))
        t = float(r.get("thickness", float("nan")))
        ok_h = hum.get("min") <= h <= hum.get("max")
        ok_d = den.get("min") <= d <= den.get("max")
        ok_t = th.get("min") <= t <= th.get("max")
        rows.append({"batch": bid, "humidity": h, "density": d, "thickness": t, "ok_h": ok_h, "ok_d": ok_d, "ok_t": ok_t})

    def over(v, mx):
        try:
            return max(0.0, round(float(v) - float(mx), 4))
        except Exception:
            return 0.0

    labels = [str(r["batch"]) for r in rows]
    hum_over = [over(r["humidity"], hum.get("max", r["humidity"])) for r in rows]
    th_over  = [over(r["thickness"], th.get("max", r["thickness"])) for r in rows]

    return {
        "tables": [{
            "title": "Batch Measurements",
            "columns": ["Batch","Humidity %","Density g/cm³","Thickness mm","Status"],
            "rows": [[r["batch"], r["humidity"], r["density"], r["thickness"],
                      "OK" if (r["ok_h"] and r["ok_d"] and r["ok_t"]) else "NON-CONFORM"]
                     for r in rows]
        }],
        "charts": [{
            "title": "Deviations over Max (positive only)",
            "type": "bar",
            "labels": labels,
            "datasets": [
                {"label": "Humidity Δ over max", "data": hum_over},
                {"label": "Thickness Δ over max", "data": th_over}
            ]
        }]
    }

def _build_process_viz(csv_path: str, yaml_path: str) -> Dict[str, Any]:
    df = pd.read_csv(csv_path)
    try:
        with open(yaml_path, "r", encoding="utf-8") as f:
            _ = yaml.safe_load(f) or {}
    except Exception:
        pass
    labels = [str(x) for x in df.index.tolist()]
    series = []
    for col in ("speed_mpm","temperature_c","density_gcm3"):
        if col in df.columns:
            series.append({"label": col, "data": [float(v) for v in df[col].tolist()]})
    return {
        "tables": [{
            "title": "Process Metrics",
            "columns": list(df.columns),
            "rows": df.fillna("").values.tolist()
        }],
        "charts": [{
            "title": "Process Time Series",
            "type": "line",
            "labels": labels,
            "datasets": series
        }]
    }

def _build_maintenance_viz(log_path: str, yaml_path: str) -> Dict[str, Any]:
    text = open(log_path, "r", encoding="utf-8", errors="ignore").read()
    lines = [ln for ln in text.splitlines() if ln.strip()]
    counts = {
        "sensor lost": len(re.findall(r"sensor\s+lost", text, flags=re.I)),
        "frequency drift": len(re.findall(r"frequency\s+drift", text, flags=re.I)),
        "overheat": len(re.findall(r"overheat", text, flags=re.I)),
        "ERROR": len(re.findall(r"\bERROR\b", text)),
        "WARN": len(re.findall(r"\bWARN(ING)?\b", text, flags=re.I)),
    }
    table_rows = []
    for ln in lines[-200:]:
        m = re.match(r"^(\d{4}-\d{2}-\d{2}[\sT]\d{2}:\d{2}:\d{2}).*(ERROR|WARN|INFO).*?:\s*(.*)$", ln)
        if m:
            table_rows.append([m.group(1), m.group(2), m.group(3)])
        else:
            table_rows.append(["—","—", ln.strip()[:200]])
    return {
        "tables": [{
            "title": "Recent Log Events",
            "columns": ["Time","Level","Message"],
            "rows": table_rows[-50:]
        }],
        "charts": [{
            "title": "Fault Counters",
            "type": "bar",
            "labels": list(counts.keys()),
            "datasets": [{"label":"Count","data": list(counts.values())}]
        }]
    }

def _build_eco_viz(csv_path: str, yaml_path: str) -> Dict[str, Any]:
    df = pd.read_csv(csv_path)
    try:
        with open(yaml_path, "r", encoding="utf-8") as f:
            _ = yaml.safe_load(f) or {}
    except Exception:
        pass
    labels = [str(x) for x in (df["batch_id"].tolist() if "batch_id" in df.columns else df.index.tolist())]
    def col(name): return [float(v) for v in df[name].tolist()] if name in df.columns else []
    return {
        "tables": [{
            "title": "Eco Metrics",
            "columns": list(df.columns),
            "rows": df.fillna("").values.tolist()
        }],
        "charts": [{
            "title": "Per-batch Metrics",
            "type": "bar",
            "labels": labels,
            "datasets": [
                {"label": "Energy kWh", "data": col("energy_kwh")},
                {"label": "Waste kg",   "data": col("waste_kg")},
                {"label": "CO₂ kg",     "data": col("co2_kg")},
            ]
        }]
    }


# -----------------------
#  Runners
# -----------------------
def _run_agent(agent_key: str, agent_factory, prompt: str) -> str:
    agent = agent_factory()
    res = agent.run(prompt)
    text = _extract_text(res).strip()
    if text:
        return text

    # Fallback Quality : rapport minimal local si le LLM renvoie vide
    if agent_key == "quality":
        src, rules = _parse_analyze_prompt(prompt)
        if src and rules and Path(src).exists() and Path(rules).exists():
            return _fallback_quality_report(_to_abs(src), _to_abs(rules))

    return "⚠️ The agent returned an empty response. Please retry or check the input files."


# -----------------------
#  Routes
# -----------------------
@app.route("/")
def index():
    return render_template("index.html")


@app.post("/api/run/<agent>")
def run_agent_api(agent: str):
    """
    POST multipart/form-data:
      - file (optionnel)
      - prompt (optionnel)
    Réponse: { ok: bool, report: str, viz?: {tables, charts} }
    """
    file = request.files.get("file")
    prompt = (request.form.get("prompt") or "").strip()

    saved_path: Optional[Path] = None
    if file and file.filename:
        saved_path = UPLOAD_DIR / file.filename
        file.save(saved_path)

    defaults = {
        "quality":     f"Analyze {saved_path or _to_abs(DATA_DIR / 'quality.csv')} using {_to_abs(KB_DIR / 'quality_rules.yaml')}",
        "process":     f"Analyze {saved_path or _to_abs(DATA_DIR / 'process.csv')} using {_to_abs(KB_DIR / 'process_rules.yaml')}",
        "maintenance": f"Analyze {saved_path or _to_abs(LOGS_DIR / 'system.log')} using {_to_abs(KB_DIR / 'maintenance_rules.yaml')}",
        "eco":         f"Analyze {saved_path or _to_abs(DATA_DIR / 'eco.csv')} using {_to_abs(KB_DIR / 'eco_targets.yaml')}",
    }

    agent_key = agent.lower()
    factories = {
        "quality": create_quality_reasoner_agent,
        "process": create_process_advisor_agent,
        "maintenance": create_maintenance_advisor_agent,
        "eco": create_eco_insight_agent,
    }

    if agent_key not in defaults:
        return jsonify({"ok": False, "error": f"Unknown agent '{agent}'."}), 400

    final_prompt = prompt or defaults[agent_key]

    try:
        report = _run_agent(agent_key, factories[agent_key], final_prompt)
        viz: Optional[Dict[str, Any]] = None

        # Construire viz si possible à partir du prompt et des fichiers réels
        src, rules = _parse_analyze_prompt(final_prompt)
        if src:
            src = _to_abs(src)
        if rules:
            rules = _to_abs(rules)

        if agent_key == "quality" and src and rules and Path(src).exists() and Path(rules).exists():
            viz = _build_quality_viz(src, rules)
        elif agent_key == "process" and src and Path(src).exists():
            viz = _build_process_viz(src, rules or "")
        elif agent_key == "maintenance" and src and Path(src).exists():
            viz = _build_maintenance_viz(src, rules or "")
        elif agent_key == "eco" and src and rules and Path(src).exists() and Path(rules).exists():
            viz = _build_eco_viz(src, rules)

        # Délimiteur de fin pour une meilleure séparation côté UI
        out_text = report.strip()
        if not out_text.endswith("--- END OF REPORT ---"):
            out_text += "\n--- END OF REPORT ---"

        return jsonify({"ok": True, "report": out_text, "viz": viz})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


# -----------------------
#  Entrée
# -----------------------
if __name__ == "__main__":
    # Démarrage en dev: http://127.0.0.1:5000
    app.run(host="0.0.0.0", port=5000, debug=True)
