# 🧠 TiHive SmartOps Module Overview

## 📋 Table of Contents

- [🔍 Module Overview](#module-overview)
- [🎯 Strategic Objective](#strategic-objective)
- [🏧 Architecture](#architecture)
- [🤖 Agent Details](#agent-details)
- [🛠️ Tools and Capabilities](#tools-and-capabilities)
- [🔌 API Integration](#api-integration)
- [💡 Usage Examples](#usage-examples)
- [🔄 Data Flow](#data-flow)
- [📦 Dependencies](#dependencies)
- [✅ Best Practices and Considerations](#best-practices-and-considerations)

---

## 🔍 Module Overview

The **TiHive SmartOps Module** is an advanced AI-powered industrial intelligence system designed to optimize operations across quality, process, maintenance, and sustainability domains.\
It integrates **four autonomous cognitive agents** to deliver real-time diagnostics, predictive recommendations, and actionable insights — transforming raw factory data into operational excellence.

### ✨ Key Features

- **🧪 Intelligent Quality Monitoring** – Detects anomalies and root causes in production data.
- **⚙️ Process Optimization** – Identifies bottlenecks and efficiency improvements.
- **🔧 Predictive Maintenance** – Anticipates equipment failures and recommends interventions.
- **🌱 Eco Efficiency Analytics** – Evaluates energy, emissions, and sustainability performance.
- **📊 Unified Cognitive Dashboard** – Streamlit-based interface for interactive visualization.
- **🧠 Knowledge-Driven Reasoning** – YAML-based rule systems for domain-specific intelligence.

---

## 🎯 Strategic Objective

The **TiHive SmartOps** initiative empowers manufacturing and industrial teams to transition from reactive decision-making to **data-driven cognitive operations**.\
By combining AI reasoning, real-time analytics, and domain knowledge bases, SmartOps delivers **sustainable productivity gains, operational reliability, and reduced environmental impact**.

---

## 🏧 Architecture

### 🏢 Module Structure

```
TiHiveSmartOpsModule/
├── Agents/
│   ├── QualityReasonerAgent
│   ├── ProcessAdvisorAgent
│   ├── MaintenanceAdvisorAgent
│   └── EcoInsightAgent
├── Data/
│   ├── CSV Inputs (quality_report.csv, process_metrics.csv, eco_data.csv)
│   └── Logs (system.log)
├── KnowledgeBase/
│   ├── quality_rules.yaml
│   ├── process_rules.yaml
│   ├── maintenance_rules.yaml
│   └── eco_targets.yaml
├── Interface/
│   └── Streamlit Dashboard (smartops_dashboard.py)
└── Utils/
    ├── safe_run()
    └── pretty()
```

### 🧩 Design Pattern

- **🌟 Modular Multi-Agent System** – Each agent operates autonomously with its own knowledge base.
- **🧠 Hybrid Reasoning** – Combines LLM reasoning (Gemini) with rule-based logic (YAML KB).
- **📊 Data-Driven** – Works directly on CSV or log data sources.
- **🌐 Streamlit UI Integration** – Unified dashboard for agent orchestration.
- **⚡ Event-Driven Processing** – Each agent executes on demand with asynchronous feedback.

---

## 🤖 Agent Details

The TiHive SmartOps Module includes **four specialized cognitive agents**:

### 🧪 Agent 1: Quality Reasoner

**Name**: `Quality Reasoner Agent`\
**Model**: `GeminiChat(model='gemini-2.5-flash')`\
**Role**: Analyze production quality data and detect anomalies.\
**Architecture**: Standalone Agent

#### 🌟 What it does

The Quality Reasoner interprets inspection data and quality reports to identify deviations, root causes, and corrective actions. It leverages statistical reasoning, pattern analysis, and a structured YAML knowledge base of quality rules.

**🔧 Primary Functions**

1. **📈 Data-Driven Quality Assessment** – Analyzes product defect ratios, deviations, and batch quality metrics.
2. **🧠 Root Cause Identification** – Correlates causes to machine parameters and process steps.
3. **🧼 Corrective Recommendation** – Suggests immediate and preventive measures with urgency levels.
4. **🧳 Quality Reporting** – Generates structured summaries with explanations and actionable insights.

**🧰 Tools**

- `safe_run()` – Executes reasoning pipeline securely.
- `TextKnowledgeBase(quality_rules.yaml)` – Provides rule context for AI reasoning.
- `pandas` – Dataframe analysis of uploaded CSV inputs.

---

### ⚙️ Agent 2: Process Advisor

**Name**: `Process Advisor Agent`\
**Model**: `Gemini(model='gemini-2.5-flash')`\
**Role**: Optimize operational processes and resource utilization.\
**Architecture**: Standalone Agent

#### 🌟 What it does

The Process Advisor analyzes production metrics to detect inefficiencies and propose optimization strategies that balance throughput, energy, and cost.

**🔧 Primary Functions**

1. **⚙️ Process Metrics Evaluation** – Analyzes process performance indicators from CSV input.
2. **🚦 Bottleneck Detection** – Identifies constraints across production stages.
3. **🧑‍🔬 Optimization Recommendation** – Suggests process adjustments and workflow improvements.
4. **📊 Priority Visualization** – Ranks recommendations by impact and urgency.

**🧰 Tools**

- `process_rules.yaml` – Knowledge base defining process constraints and thresholds.
- `plotly.express` – Visual representation of recommendation priorities.
- `pandas` – Metrics computation and filtering.

---

### 🔧 Agent 3: Maintenance Advisor

**Name**: `Maintenance Advisor Agent`\
**Model**: `GeminiChat(model='gemini-2.5-flash')`\
**Role**: Detect early signs of equipment degradation and plan maintenance actions.\
**Architecture**: Standalone Agent

#### 🌟 What it does

This agent reviews system logs and sensor patterns to detect anomalies, predict potential failures, and suggest repair or inspection actions.

**🔧 Primary Functions**

1. **🛠️ Log Diagnostics** – Parses system logs for fault signatures and anomalies.
2. **🔍 Root Cause Mapping** – Associates fault types with known maintenance categories.
3. **🗓️ Preventive Maintenance Planning** – Suggests optimal maintenance windows.
4. **📋 Maintenance Reporting** – Provides issue summaries with severity and timeframe.

**🧰 Tools**

- `maintenance_rules.yaml` – Structured fault library and intervention rules.
- `log parser` – Text processing and pattern recognition utilities.
- `pandas` / `re` – Data and regex parsing for structured extraction.

---

### 🌱 Agent 4: Eco Insight

**Name**: `Eco Insight Agent`\
**Model**: `GeminiChat(model='gemini-2.5-flash')`\
**Role**: Evaluate sustainability metrics and environmental performance.\
**Architecture**: Standalone Agent

#### 🌟 What it does

The Eco Insight Agent evaluates ecological performance, focusing on emission levels, compliance rates, and energy efficiency goals defined in YAML targets.

**🔧 Primary Functions**

1. **♻️ Eco Data Analysis** – Reads eco\_data.csv and calculates compliance metrics.
2. **📉 Emission Estimation** – Quantifies total and batch-wise emissions.
3. **🌍 Compliance Classification** – Labels batches as Compliant, Partial, or Non-compliant.
4. **📈 Trend Visualization** – Plots environmental performance over time.

**🧰 Tools**

- `eco_targets.yaml` – Sustainability benchmarks and emission thresholds.
- `plotly.express` – Visualization of compliance rates.
- `pandas` – Batch-wise KPI aggregation.

---

## 🛠️ Tools and Capabilities

### 📊 Data Interfaces

- **CSV Importers** – Quality, Process, and Eco datasets.
- **Log Parsers** – For maintenance diagnostics.
- **YAML Knowledge Bases** – Structured expert rule sets for reasoning.

### 🧠 Reasoning Engine

- **Gemini AI Model** – Cognitive reasoning and natural language synthesis.
- **safe\_run() Utility** – Ensures stable agent execution and error handling.
- **pretty() Function** – Formats model outputs into human-readable JSON.

### 💻 Visualization Layer

- **Streamlit Framework** – Interactive dashboard UI.
- **Plotly Express** – Dynamic chart generation.
- **Custom CSS Styling** – Branded UI consistency.

---

## 🔌 API Integration

### ⚙️ Core System Integration

- **Language Model**: Gemini via Google API
- **Frontend Framework**: Streamlit
- **Execution Layer**: Python Agents via `TiHiveSmartOps.py`
- **Knowledge Base Storage**: Local YAML

### 📡 Data Flow (API/Agent Invocation)

1. User selects agent in Streamlit sidebar.
2. System loads respective knowledge base and dataset.
3. Agent runs through `safe_run()` and parses reasoning output.
4. Structured JSON returned to the dashboard for visualization.

### 🔐 Configuration Parameters

```bash
GEMINI_API_KEY=your_google_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
DATA_PATH=./data/
KB_PATH=./kb/
STREAMLIT_PORT=8501
```

---

## 💡 Usage Examples

### 🧪 Quality Reasoner Example

```
Input: Analyze quality_report.csv for defect patterns.
Process: Agent parses CSV, applies rules, and identifies root causes.
Output: Diagnosis summary, possible causes, and recommendations.
```

### ⚙️ Process Advisor Example

```
Input: process_metrics.csv
Process: Detects bottlenecks, prioritizes improvement areas.
Output: Bar chart of priorities and optimization insights.
```

### 🔧 Maintenance Advisor Example

```
Input: system.log
Process: Scans for errors, maps to known fault types.
Output: Maintenance summary with root cause and timeframe.
```

### 🌱 Eco Insight Example

```
Input: eco_data.csv
Process: Calculates compliance and emission levels.
Output: Eco performance chart and global diagnosis.
```

---

## 🔄 Data Flow

### 📥 Input Processing

1. User uploads or references CSV/log file.
2. System validates and loads the data into DataFrame or parser.
3. Relevant YAML rules are loaded as the knowledge context.

### 🧠 Analysis

1. Data is processed via Gemini reasoning + rule base.
2. Agents extract patterns, evaluate conditions, and produce structured outputs.
3. Outputs are formatted through `pretty()` for JSON display.

### 📤 Output Visualization

1. Streamlit dashboard renders metrics and charts.
2. Explanations, causes, and recommendations displayed with styled components.
3. Optional export (future extension: PDF or CSV summaries).

---

## 📦 Dependencies

### 🏧 Core Libraries

```python
streamlit>=1.37.0
pandas>=2.2.0
plotly>=5.19.0
pyyaml>=6.0
google-generativeai>=0.5.0
```

### ⚙️ Internal Utilities

```python
utils.py  # safe_run(), pretty()
Agents/TiHiveSmartOps.py  # Agent creation functions
```

### 🔐 Environment Configuration

```bash
GEMINI_API_KEY=your_api_key_here
DATA_DIR=./data
KB_DIR=./kb
```

---

## ✅ Best Practices and Considerations

### 🔒 Security and Data Protection

- Sensitive API keys stored in `.env`.
- Data processed locally — no external uploads.
- Optional anonymization for sensitive logs.

### ⚡ Performance

- Lightweight CSV parsing for fast load times.
- Caching of parsed results in Streamlit session state.
- Asynchronous agent invocation planned for scalability.

### 🌟 Accuracy and Reliability

- Knowledge bases versioned for traceability.
- Validation of CSV schema before reasoning.
- Graceful error handling through `safe_run()`.

### 🌍 Sustainability Focus

- Eco Insight Agent promotes green operations.
- Supports integration with real factory emission sensors.
- Encourages continuous efficiency tracking.

---

*The TiHive SmartOps Module integrates advanced AI reasoning, domain-specific knowledge, and intuitive visualization to redefine operational intelligence. By merging machine cognition with human oversight, SmartOps provides the foundation for sustainable, data-driven industrial transformation.*

