from Agents.TiHiveSmartOps import (
    create_quality_reasoner_agent,
    create_process_advisor_agent,
    create_maintenance_advisor_agent,
    create_eco_insight_agent
)
from utils import pretty, safe_run  # ✅ Nouvelle importation propre
import time


def run_agent(agent, description, command):
    """Exécute un agent avec protection contre les erreurs Gemini."""
    try:
        print(f"🔹 Running {description} ...")
        content = safe_run(agent, command)
        print(f"{description.upper()} RESULT:\n", pretty(content), "\n")
    except Exception as e:
        print(f"⚠️ Error running {description}: {e}")


def main():
    print("=== TiHive SmartOps Cognitive AI Suite (Gemini) ===\n")

    # === 1️⃣ QUALITY REASONER ===
    q = create_quality_reasoner_agent()
    run_agent(q, "Quality Reasoner Agent", "Analyze data/quality_report.csv using kb/quality_rules.yaml")
    time.sleep(5)

    # === 2️⃣ PROCESS ADVISOR ===
    p = create_process_advisor_agent()
    run_agent(p, "Process Advisor Agent", "Analyze data/process_metrics.csv using kb/process_rules.yaml")
    time.sleep(5)

    # === 3️⃣ MAINTENANCE ADVISOR ===
    m = create_maintenance_advisor_agent()
    run_agent(m, "Maintenance Advisor Agent", "Analyze logs/system.log using kb/maintenance_rules.yaml")
    time.sleep(5)

    # === 4️⃣ ECO INSIGHT ===
    e = create_eco_insight_agent()
    run_agent(e, "Eco Insight Agent", "Analyze data/eco_data.csv using kb/eco_targets.yaml")
    print("\n✅ Analysis completed successfully!")


if __name__ == "__main__":
    main()
