# DevPilot

AI-powered PM/PMO consulting SaaS. Project planning, WBS generation, risk analysis, weekly reports, and vendor evaluation.

## Features

1. **Project Planner** - PMBOK/Agile-based project plan generation with WBS, milestones, Gantt chart data
2. **Risk Analyzer** - EVM metrics (SPI, CPI, EAC, ETC), delay prediction, risk register
3. **Report Generator** - Bilingual (JA/EN) weekly reports with executive summary + detailed version
4. **WBS Generator** - 6 project type templates (Web, Infra, ERP, Mobile, AI/ML, Data Platform), PERT estimation, critical path
5. **Vendor Evaluator** - RFP template generation, scoring matrix, 5-year TCO comparison

## Quick Start

```bash
pip install -r requirements.txt

# API server
uvicorn app.main:app --reload

# Streamlit UI
streamlit run ui/streamlit_app.py

# Tests
pytest tests/ -q
```

## Project Structure

```
app/
  main.py              # FastAPI application
  models.py            # Pydantic data models
  services/
    project_planner.py # Project planning AI
    risk_analyzer.py   # Risk analysis AI
    report_generator.py# Weekly report generation
    wbs_generator.py   # WBS auto-generation
    vendor_evaluator.py# Vendor evaluation AI
  knowledge/
    pmbok_framework.py # PMBOK 7th Edition principles & domains
    agile_framework.py # Scrum / Kanban / SAFe
    project_templates.py # 6 WBS templates
    evm_formulas.py    # EVM calculation formulas
  db/
    database.py        # SQLAlchemy database layer
ui/
  streamlit_app.py     # Streamlit dashboard
tests/
  test_project_planner.py
  test_risk_analyzer.py
  test_report_generator.py
  test_wbs_generator.py
  test_vendor_evaluator.py
docs/
  index.html           # Landing page
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/projects/plan` | Create project plan |
| POST | `/api/v1/projects/wbs` | Generate WBS |
| POST | `/api/v1/risks/analyze` | Run risk analysis |
| POST | `/api/v1/reports/weekly` | Generate weekly report |
| POST | `/api/v1/vendors/evaluate` | Evaluate vendors |
| GET | `/api/v1/projects` | List projects |
| GET | `/api/v1/projects/{id}` | Get project details |

## PilotStack

Part of the [PilotStack](https://github.com/mattyopon) suite of AI-powered consulting tools.

---

(c) 2026 PilotStack
