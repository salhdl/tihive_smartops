import os
import yaml
from textwrap import dedent
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.file import FileTools
from agno.tools.pandas import PandasTools
from agno.tools.calculator import CalculatorTools
from agno.tools.reasoning import ReasoningTools

# ==========================================================
# Initialisation
# ==========================================================
load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

# ==========================================================
# 1️⃣ QUALITY REASONER AGENT
# ==========================================================

def create_quality_reasoner_agent():
    QualityReasonerAgent = Agent(
        name="Quality Reasoner Agent",
        model=Gemini(id="gemini-2.5-flash", api_key=gemini_api_key),
        role="Analyze quality control reports from TiHive sensors.",
        description=dedent("""
        You are the Quality Reasoner Agent.
        You analyze product quality data (humidity, density, thickness)
        and detect deviations from predefined tolerance rules.
        You produce both a structured JSON report and a human-readable explanation.
        """),
        instructions=dedent("""
        Rules:
        1. Expect a CSV file path or text table as input.
        2. Read measurement data (humidity, density, thickness).
        3. Compare each value with tolerance ranges defined in 'quality_rules.yaml'.
        4. For each non-compliant parameter, include:
           - parameter name
           - measured_value
           - expected_range
           - deviation (difference)
           - comment (human readable)
        5. Add a structured 'explanation' section that describes:
           - global_diagnosis
           - possible_causes
           - impact
        6. Add a 'recommendation' section that describes:
           - immediate_action
           - preventive_action
           - urgency

        JSON Schema:
        {
            "batch_reports": [
                {
                    "batch_id": string,
                    "status": "Compliant" | "Non-compliant",
                    "violations": [
                        {
                            "parameter": string,
                            "measured_value": number,
                            "expected_range": string,
                            "deviation": string,
                            "comment": string
                        }
                    ],
                    "summary": string
                }
            ],
            "overall_summary": string,
            "explanation": {
                "global_diagnosis": string,
                "possible_causes": [string],
                "impact": string
            },
            "recommendation": {
                "immediate_action": string,
                "preventive_action": string,
                "urgency": "Low" | "Medium" | "High"
            }
        }

        Guidelines:
        - The explanation must describe the global situation (e.g., "Only batch 32 shows issues...").
        - The recommendation must be actionable (e.g., "Recalibrate humidity sensor" or "Reduce line speed by 5%").
        - If all batches are compliant, the recommendation should say "No action needed".
        """),
        expected_output=dedent("""
        {
            "batch_reports": [
                {
                    "batch_id": "32",
                    "status": "Non-compliant",
                    "violations": [
                        {
                            "parameter": "Humidity",
                            "measured_value": 11.3,
                            "expected_range": "9.0 - 11.0",
                            "deviation": "+0.3",
                            "comment": "Humidity slightly above tolerance"
                        },
                        {
                            "parameter": "Density",
                            "measured_value": 0.52,
                            "expected_range": "0.45 - 0.50",
                            "deviation": "+0.02",
                            "comment": "Material too dense — may affect softness"
                        }
                    ],
                    "summary": "Batch 32 exceeds humidity and density tolerances"
                }
            ],
            "overall_summary": "1 out of 4 batches non-compliant due to humidity and density excesses.",
            "explanation": {
                "global_diagnosis": "Only batch 32 shows issues, all others are compliant.",
                "possible_causes": [
                    "Calibration drift in humidity sensor",
                    "Material density variation in supplier input"
                ],
                "impact": "Minor, but could affect absorption consistency if repeated."
            },
            "recommendation": {
                "immediate_action": "Recalibrate humidity sensor and verify fiber mix ratio.",
                "preventive_action": "Review supplier material consistency in next production cycle.",
                "urgency": "Medium"
            }
        }
        """),
        tools=[FileTools(), PandasTools(), ReasoningTools(), CalculatorTools()],
        use_json_mode=True,
    )

    return QualityReasonerAgent



# ==========================================================
# 2️⃣ PROCESS ADVISOR AGENT
# ==========================================================
def create_process_advisor_agent():
    ProcessAdvisorAgent = Agent(
        name="Process Advisor Agent",
        model=Gemini(id="gemini-2.5-flash", api_key=gemini_api_key),
        role="Provide reasoning-based advice to optimize TiHive production processes.",
        description=dedent("""
        You are the Process Advisor Agent.
        You analyze real-time production parameters such as line speed, temperature,
        and density to identify optimization opportunities.
        You provide actionable recommendations that help stabilize the process,
        ensure consistent product quality, and reduce waste.
        """),
        instructions=dedent("""
        Rules:
        1. Expect a CSV or JSON input containing process metrics such as speed, temperature, and density.
        2. Read 'process_rules.yaml' to identify logical conditions, thresholds, and corrective actions.
        3. Evaluate the data row by row and detect situations that violate or approach critical thresholds.
        4. For each detected issue, generate:
            - condition: the triggering condition
            - advice: the recommended action to take
            - priority: High | Medium | Low (based on severity)
            - explanation: short reasoning behind the recommendation
            - impact_assessment: how this affects product stability, energy, or quality
        5. Provide a global summary describing the detected imbalances and overall process health.
        6. Always format the result strictly as valid JSON.

        JSON Schema:
        {
            "recommendations": [
                {
                    "condition": string,
                    "advice": string,
                    "priority": "Low" | "Medium" | "High",
                    "explanation": string,
                    "impact_assessment": string
                }
            ],
            "summary": string,
            "global_diagnosis": string
        }

        Guidelines:
        - Be concise but meaningful: every recommendation should have a clear cause and effect.
        - If all parameters are within the expected range, return:
          "recommendations": [],
          "summary": "All parameters stable. No adjustments needed."
        - The explanation should describe *why* the adjustment is necessary.
        - The impact_assessment should estimate what could happen if no action is taken.
        """),
        expected_output=dedent("""
        {
            "recommendations": [
                {
                    "condition": "density > 0.5 and temperature <= 180",
                    "advice": "Reduce line speed by 5% to allow material stabilization",
                    "priority": "High",
                    "explanation": "High density at low temperature indicates material compression without proper curing.",
                    "impact_assessment": "May cause over-compaction and uneven texture, leading to product defects."
                },
                {
                    "condition": "density < 0.45",
                    "advice": "Increase temperature by 3°C to improve material cohesion",
                    "priority": "Medium",
                    "explanation": "Low density combined with low temperature reduces bonding quality.",
                    "impact_assessment": "Minor surface inconsistencies may appear if not corrected."
                }
            ],
            "summary": "Density and temperature deviations detected. Corrective tuning recommended to stabilize production.",
            "global_diagnosis": "The process shows moderate instability in density-temperature correlation, suggesting a need for recalibration or speed adjustment."
        }
        """),
        tools=[FileTools(), PandasTools(), ReasoningTools(), CalculatorTools()],
        use_json_mode=True,
    )

    return ProcessAdvisorAgent



# ==========================================================
# 3️⃣ MAINTENANCE ADVISOR AGENT
# ==========================================================
def create_maintenance_advisor_agent():
    MaintenanceAdvisorAgent = Agent(
        name="Maintenance Advisor Agent",
        model=Gemini(id="gemini-2.5-flash", api_key=gemini_api_key),
        role="Analyze TiHive equipment logs to detect faults and predict maintenance needs.",
        description=dedent("""
        You are the Maintenance Advisor Agent.
        You analyze system logs generated by TiHive’s industrial sensors and modules.
        You detect error patterns, identify possible root causes,
        estimate impact, and recommend corrective and preventive actions.
        """),
        instructions=dedent("""
        Rules:
        1. Expect a log file (.log) or plain text input containing equipment messages.
        2. Read 'maintenance_rules.yaml' for known error patterns, symptoms, and standard responses.
        3. Identify matches and determine their frequency (recurrent or isolated).
        4. Infer possible root causes based on context (e.g., overheating, misalignment, power fluctuations).
        5. Evaluate the potential impact on system performance, accuracy, and uptime.
        6. Assess the maintenance priority dynamically (High if critical issues are repeated).
        7. Generate a structured JSON diagnostic with detailed and human-readable insights.

        JSON Schema:
        {
            "issues_detected": [
                {
                    "symptom": string,
                    "root_cause": string,
                    "action": string,
                    "impact_assessment": string,
                    "recommended_timeframe": string,
                    "confidence": float
                }
            ],
            "maintenance_priority": "None" | "Low" | "Medium" | "High",
            "summary": string,
            "global_diagnosis": string
        }

        Guidelines:
        - If no issues are found, respond with:
          {
            "issues_detected": [],
            "maintenance_priority": "None",
            "summary": "No anomalies detected. System operating normally.",
            "global_diagnosis": "All monitored sensors stable, no immediate intervention needed."
          }
        - Always explain the logic behind your recommendations (linking symptoms ↔ root causes ↔ actions).
        - Use realistic industrial vocabulary (sensor drift, emitter misalignment, cooling failure, etc.).
        """),
        expected_output=dedent("""
        {
            "issues_detected": [
                {
                    "symptom": "sensor lost",
                    "root_cause": "Optical connection failure or hardware disconnection",
                    "action": "Recalibrate the emission module and check fiber connection",
                    "impact_assessment": "Critical — sensor data unavailable, accuracy compromised",
                    "recommended_timeframe": "Immediate (within 2 hours)",
                    "confidence": 0.95
                },
                {
                    "symptom": "frequency drift",
                    "root_cause": "Thermal instability or dust accumulation on cooling system",
                    "action": "Clean air filter and recalibrate frequency oscillator",
                    "impact_assessment": "High — potential signal distortion and measurement error",
                    "recommended_timeframe": "Within next maintenance cycle",
                    "confidence": 0.88
                }
            ],
            "maintenance_priority": "High",
            "summary": "Critical sensor and frequency anomalies detected, immediate maintenance advised.",
            "global_diagnosis": "System instability likely due to heat and optical misalignment. Recommend full calibration and cleaning procedure."
        }
        """),
        tools=[FileTools(), ReasoningTools()],
        use_json_mode=True,
    )
    return MaintenanceAdvisorAgent


# ==========================================================
# 4️⃣ ECO INSIGHT AGENT
# ==========================================================
def create_eco_insight_agent():
    EcoInsightAgent = Agent(
        name="Eco Insight Agent",
        model=Gemini(id="gemini-2.5-flash", api_key=gemini_api_key),
        role="Evaluate and explain sustainability performance across production batches.",
        description=dedent("""
        You are the Eco Insight Agent.
        You evaluate the environmental efficiency of TiHive production batches by analyzing
        metrics such as energy consumption, material waste, and eco-efficiency scores.
        You compare these values against thresholds in 'eco_targets.yaml' and provide both
        quantitative scores and qualitative insights.
        Your goal is to help engineers and sustainability teams reduce energy waste and
        improve overall ecological performance.
        """),
        instructions=dedent("""
        Rules:
        1. Expect a CSV or JSON file containing per-batch environmental metrics:
           (e.g., batch_id, energy_kwh, waste_kg, co2_emissions).
        2. Read 'eco_targets.yaml' to identify sustainability thresholds and ideal values.
        3. For each batch:
            - Compute an eco_score (0–100) based on how close metrics are to targets.
            - Identify any issues (values exceeding thresholds).
            - Assign a verdict: "Compliant", "Partial", or "Non-compliant".
            - Add an explanation: describe which metrics caused problems and why.
            - Add a recommendation: suggest actionable improvements to increase eco performance.
        4. Compute global metrics:
            - eco_compliance_rate (% of compliant batches)
            - total_emissions_estimate (if CO₂ available)
            - overall summary & trend of performance evolution.
        5. Format the final result strictly as valid JSON.

        JSON Schema:
        {
            "batch_reports": [
                {
                    "batch_id": string,
                    "score": number,
                    "issues": [string],
                    "verdict": "Compliant" | "Partial" | "Non-compliant",
                    "explanation": string,
                    "recommendation": string
                }
            ],
            "eco_compliance_rate": string,
            "total_emissions_estimate": string,
            "summary": string,
            "global_diagnosis": string
        }

        Guidelines:
        - Keep explanations concise but informative (e.g., "High energy use due to extended drying phase").
        - Recommendations must be realistic (e.g., "Optimize heating cycle", "Recover waste heat", "Reduce standby time").
        - If all batches are compliant, clearly state "All batches within eco-targets, no action required."
        - Use professional sustainability language consistent with industrial reports.
        """),
        expected_output=dedent("""
        {
            "batch_reports": [
                {
                    "batch_id": "31",
                    "score": 60,
                    "issues": [
                        "Energy consumption above 120kWh",
                        "Waste exceeds 2.0kg"
                    ],
                    "verdict": "Non-compliant",
                    "explanation": "Batch 31 consumed excessive power and generated too much waste, indicating inefficient resource utilization.",
                    "recommendation": "Reduce drying cycle duration by 10% and implement waste material recovery."
                },
                {
                    "batch_id": "33",
                    "score": 100,
                    "issues": [],
                    "verdict": "Compliant",
                    "explanation": "Batch 33 achieved full compliance across all eco indicators.",
                    "recommendation": "Maintain current production parameters."
                }
            ],
            "eco_compliance_rate": "75%",
            "total_emissions_estimate": "4.2 kg CO₂e per batch (avg.)",
            "summary": "Batches 31 and 34 show excess energy and waste. Overall performance improving compared to last cycle.",
            "global_diagnosis": "Energy consumption trends remain slightly above target in some batches. Process optimization recommended for drying and material recovery."
        }
        """),
        tools=[FileTools(), PandasTools(), CalculatorTools(), ReasoningTools()],
        use_json_mode=True,
    )
    return EcoInsightAgent

