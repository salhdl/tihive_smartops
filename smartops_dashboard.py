import streamlit as st
import json
import pandas as pd
import plotly.express as px
from utils import safe_run, pretty
from Agents.TiHiveSmartOps import (
    create_quality_reasoner_agent,
    create_process_advisor_agent,
    create_maintenance_advisor_agent,
    create_eco_insight_agent
)

# === CONFIGURATION ===
st.set_page_config(page_title="TiHive SmartOps Dashboard", page_icon="🧠", layout="wide")

# === STYLE GLOBAL ===
st.markdown("""
<style>
    body {
        background-color: #f9fafb;
        color: #111;
    }
    .title {
        font-size: 2.3em;
        font-weight: 800;
        text-align: center;
        color: #111;
        margin-top: -10px;
        margin-bottom: 10px;
    }
    .subtitle {
        text-align: center;
        color: #374151;
        font-size: 1.05em;
        margin-bottom: 35px;
    }
    .section-box {
        background-color: white;
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.07);
        padding: 20px 25px;
        margin-bottom: 20px;
    }
    .metric-box {
        background-color: #f1f5f9;
        border-radius: 10px;
        padding: 10px;
        margin: 5px 0;
    }
    .result-title {
        font-size: 1.2em;
        font-weight: bold;
        color: #111;
        margin-top: 20px;
        margin-bottom: 10px;
    }
    .explanation, .recommendation {
        color: #111;
        font-size: 1.05em;
        background: #f9fafb;
        border-left: 5px solid #2563eb;
        padding: 10px 15px;
        border-radius: 6px;
        margin-bottom: 10px;
    }
    .recommendation {
        border-left-color: #22c55e;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">🧠 TiHive SmartOps Cognitive Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI-powered insights for Quality • Process • Maintenance • Sustainability</div>', unsafe_allow_html=True)

# === SIDEBAR ===
st.sidebar.header("⚙️ Choose Section")
agent_name = st.sidebar.selectbox(
    "Select AI Agent / Overview:",
    ["SmartOps Overview", "Quality Reasoner", "Process Advisor", "Maintenance Advisor", "Eco Insight"]
)
st.sidebar.info("Developed with ❤️ by ENSA Fès – SmartOps AI")

# === RUN WRAPPER ===
def run_agent_streamlit(agent_creator, description, command):
    with st.spinner(f"🤖 Running {description} ..."):
        try:
            agent = agent_creator()
            content = safe_run(agent, command)
            if not content:
                st.warning("⚠️ No content returned. Possibly due to API quota or empty response.")
                return None
            parsed = json.loads(pretty(content))
            st.success(f"✅ {description} completed successfully!")
            return parsed
        except Exception as e:
            st.error(f"❌ Error running {description}: {e}")
            return None


# 🧭 === 0️⃣ SMARTOPS OVERVIEW ===
if agent_name == "SmartOps Overview":
    st.subheader("📊 SmartOps Global Overview")
    st.markdown(
        """
        <div class="section-box">
        <p><b>TiHive SmartOps</b> est une plateforme cognitive conçue pour l’analyse intelligente de la qualité, des processus, de la maintenance et de la durabilité.</p>

        <p>Grâce à l’intégration de modèles d’intelligence artificielle et de bases de connaissances spécialisées, SmartOps aide les ingénieurs à :</p>
        <ul>
            <li>🧪 Surveiller la qualité et identifier les défauts critiques.</li>
            <li>⚙️ Optimiser les paramètres de production en temps réel.</li>
            <li>🔧 Détecter les pannes avant qu’elles n’affectent la production.</li>
            <li>🌱 Réduire l’impact environnemental et améliorer la conformité.</li>
        </ul>

        <p>Chaque module fonctionne de manière autonome, mais les données croisées permettent d’obtenir une <b>vision globale intelligente</b> de la performance industrielle.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # === Mini Dashboard de synthèse ===
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🧪 Quality Alerts", "12", "+3 today")
    with col2:
        st.metric("⚙️ Process Efficiency", "94%", "+2% vs last week")
    with col3:
        st.metric("🔧 Active Maintenance Tasks", "5", "2 critical")
    with col4:
        st.metric("🌱 Eco Compliance", "88%", "↗ Improving")

    # === Graphique exemple ===
    data = pd.DataFrame({
        "Module": ["Quality", "Process", "Maintenance", "Eco"],
        "Performance": [86, 92, 78, 88]
    })
    fig = px.bar(data, x="Module", y="Performance", color="Module",
                 title="Global Performance Overview",
                 color_discrete_map={
                     "Quality": "#2563eb",
                     "Process": "#f59e0b",
                     "Maintenance": "#22c55e",
                     "Eco": "#10b981"
                 })
    st.plotly_chart(fig, config={"responsive": True})


    st.markdown(
        """
        <div class="section-box">
        <p>➡️ Sélectionne un agent dans la barre latérale pour explorer ses analyses détaillées :</p>
        <ul>
            <li>🧪 <b>Quality Reasoner</b> – contrôle qualité et diagnostic.</li>
            <li>⚙️ <b>Process Advisor</b> – recommandations d’optimisation.</li>
            <li>🔧 <b>Maintenance Advisor</b> – maintenance prédictive.</li>
            <li>🌱 <b>Eco Insight</b> – durabilité et empreinte environnementale.</li>
        </ul>
        </div>
        """,
        unsafe_allow_html=True
    )



# 1️⃣ QUALITY
elif agent_name == "Quality Reasoner":
    st.subheader("🧪 Quality Reasoner Agent")
    
    uploaded_file = st.file_uploader("📤 Upload your Quality CSV file", type=["csv"])
    if uploaded_file is not None:
        df_uploaded = pd.read_csv(uploaded_file)
        st.dataframe(df_uploaded.head(), width="stretch")

    if st.button("▶️ Run Quality Analysis"):
        result = run_agent_streamlit(
            create_quality_reasoner_agent,
            "Quality Reasoner Agent",
            "Analyze data/quality_report.csv using kb/quality_rules.yaml"
        )
        if result:
            with st.container():
                st.markdown('<div class="section-box">', unsafe_allow_html=True)
                st.markdown('<div class="result-title">📊 Quality Control Summary</div>', unsafe_allow_html=True)
                st.json(result)
                exp = result.get("explanation", {})
                rec = result.get("recommendation", {})

                if exp:
                    st.markdown('<div class="result-title">🧠 Explanation</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="explanation"><b>Global diagnosis:</b> {exp.get("global_diagnosis","")}</div>', unsafe_allow_html=True)
                    if exp.get("possible_causes"):
                        st.markdown(f'<div class="explanation"><b>Possible causes:</b> {", ".join(exp["possible_causes"])}</div>', unsafe_allow_html=True)
                    if exp.get("impact"):
                        st.markdown(f'<div class="explanation"><b>Impact:</b> {exp["impact"]}</div>', unsafe_allow_html=True)

                if rec:
                    st.markdown('<div class="result-title">🩺 Recommendation</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="recommendation"><b>Immediate action:</b> {rec.get("immediate_action","")}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="recommendation"><b>Preventive action:</b> {rec.get("preventive_action","")}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="recommendation"><b>Urgency:</b> {rec.get("urgency","")}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)


# 2️⃣ PROCESS
elif agent_name == "Process Advisor":
    st.subheader("⚙️ Process Advisor Agent")
    
    uploaded_file = st.file_uploader("📤 Upload your Process CSV file", type=["csv"])
    if uploaded_file is not None:
        df_uploaded = pd.read_csv(uploaded_file)
        st.dataframe(df_uploaded.head(), width="stretch")

    if st.button("▶️ Run Process Optimization"):
        result = run_agent_streamlit(
            create_process_advisor_agent,
            "Process Advisor Agent",
            "Analyze data/process_metrics.csv using kb/process_rules.yaml"
        )
        if result:
            st.markdown('<div class="section-box">', unsafe_allow_html=True)
            df = pd.DataFrame(result["recommendations"])
            st.dataframe(df, width="stretch")
            fig = px.bar(df, x="condition", y="priority", color="priority",
                         title="Process Recommendations Priority",
                         color_discrete_map={"High":"red","Medium":"orange","Low":"green"})
            st.plotly_chart(fig, config={"responsive": True})
            st.markdown(f'<div class="result-title">🧠 Summary</div><div class="explanation">{result["summary"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="result-title">🔍 Global Diagnosis</div><div class="recommendation">{result["global_diagnosis"]}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)


# 3️⃣ MAINTENANCE
elif agent_name == "Maintenance Advisor":
    st.subheader("🔧 Maintenance Advisor Agent")

    uploaded_file = st.file_uploader("📤 Upload your System Log", type=["log", "txt"])
    if uploaded_file is not None:
        st.text_area("📄 Log Preview", uploaded_file.read().decode("utf-8")[:800])

    if st.button("▶️ Run Maintenance Diagnostics"):
        result = run_agent_streamlit(
            create_maintenance_advisor_agent,
            "Maintenance Advisor Agent",
            "Analyze logs/system.log using kb/maintenance_rules.yaml"
        )
        if result:
            st.markdown('<div class="section-box">', unsafe_allow_html=True)
            for issue in result.get("issues_detected", []):
                with st.expander(f"🛠️ {issue['symptom'].capitalize()}"):
                    st.write(f"**Root cause:** {issue['root_cause']}")
                    st.write(f"**Action:** {issue['action']}")
                    st.write(f"**Impact:** {issue['impact_assessment']}")
                    st.write(f"**Recommended timeframe:** {issue['recommended_timeframe']}")
            st.markdown(f'<div class="result-title">🧠 Summary</div><div class="explanation">{result["summary"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="result-title">🔍 Global Diagnosis</div><div class="recommendation">{result["global_diagnosis"]}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)


# 4️⃣ ECO
elif agent_name == "Eco Insight":
    st.subheader("🌱 Eco Insight Agent")

    uploaded_file = st.file_uploader("📤 Upload your Eco Data CSV file", type=["csv"])
    if uploaded_file is not None:
        df_uploaded = pd.read_csv(uploaded_file)
        st.dataframe(df_uploaded.head(), width="stretch")
    if st.button("▶️ Run Eco Evaluation"):
        result = run_agent_streamlit(
            create_eco_insight_agent,
            "Eco Insight Agent",
            "Analyze data/eco_data.csv using kb/eco_targets.yaml"
        )
        if result:
            st.markdown('<div class="section-box">', unsafe_allow_html=True)
            st.metric("♻️ Eco Compliance Rate", result.get("eco_compliance_rate", "N/A"))
            st.metric("🌍 Total Emissions", result.get("total_emissions_estimate", "Unknown"))
            df = pd.DataFrame(result["batch_reports"])
            st.dataframe(df[["batch_id", "score", "verdict"]], width="stretch")
            fig = px.bar(df, x="batch_id", y="score", color="verdict",
                         color_discrete_map={"Compliant":"green","Partial":"orange","Non-compliant":"red"},
                         title="Eco Compliance by Batch")
            st.plotly_chart(fig, config={"responsive": True})
            st.markdown(f'<div class="result-title">🌿 Summary</div><div class="explanation">{result["summary"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="result-title">🧠 Global Diagnosis</div><div class="recommendation">{result["global_diagnosis"]}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
