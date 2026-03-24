"""DevPilot FastAPI メインアプリケーション."""

from __future__ import annotations

from datetime import date
from typing import Any

from fastapi import FastAPI, HTTPException

from app.db.database import Database
from app.models import (
    ProjectInput,
    RFPRequirement,
    TaskProgress,
    VendorProposal,
    WeeklyReportInput,
)
from app.services.project_planner import create_project_plan, get_project_summary
from app.services.report_generator import generate_weekly_report
from app.services.risk_analyzer import analyze_risks
from app.services.vendor_evaluator import evaluate_vendors
from app.services.wbs_generator import generate_wbs

app = FastAPI(
    title="DevPilot",
    description="PM/PMO代替AI SaaS - プロジェクト管理の自動化",
    version="0.1.0",
)

db = Database()
db.create_tables()


@app.get("/")
def root() -> dict[str, str]:
    """ルートエンドポイント."""
    return {"service": "DevPilot", "version": "0.1.0", "status": "running"}


@app.get("/health")
def health_check() -> dict[str, str]:
    """ヘルスチェック."""
    return {"status": "healthy"}


@app.post("/api/v1/projects/plan")
def plan_project(project_input: ProjectInput) -> dict[str, Any]:
    """プロジェクト計画を作成."""
    plan = create_project_plan(project_input)
    summary = get_project_summary(plan)

    # DB保存
    project_data = {
        "name": project_input.name,
        "description": project_input.description,
        "project_type": project_input.project_type.value,
        "methodology": project_input.methodology.value,
        "start_date": project_input.start_date,
        "target_end_date": project_input.target_end_date,
        "team_size": project_input.team_size,
        "budget_jpy": project_input.budget_jpy,
        "plan": plan.model_dump(mode="json"),
    }
    project_id = db.save_project(project_data)

    return {
        "project_id": project_id,
        "summary": summary,
        "plan": plan.model_dump(mode="json"),
    }


@app.post("/api/v1/projects/wbs")
def generate_wbs_endpoint(project_input: ProjectInput) -> dict[str, Any]:
    """WBSを生成."""
    result = generate_wbs(
        project_type=project_input.project_type,
        project_name=project_input.name,
        start_date=project_input.start_date,
    )
    return {
        "template_name": result["template_name"],
        "total_estimated_days": result["total_estimated_days"],
        "tasks": [t.model_dump(mode="json") for t in result["tasks"]],
        "milestones": [m.model_dump(mode="json") for m in result["milestones"]],
        "critical_path": result["critical_path"],
        "phases": [p.model_dump(mode="json") for p in result["phases"]],
        "gantt_data": [g.model_dump(mode="json") for g in result["gantt_data"]],
    }


@app.post("/api/v1/risks/analyze")
def analyze_risks_endpoint(
    tasks: list[TaskProgress],
    reference_date: date | None = None,
) -> dict[str, Any]:
    """リスク分析を実行."""
    if not tasks:
        raise HTTPException(status_code=400, detail="タスクリストが空です")
    result = analyze_risks(tasks, reference_date)
    return result.model_dump(mode="json")


@app.post("/api/v1/reports/weekly")
def generate_report(report_input: WeeklyReportInput) -> dict[str, Any]:
    """週次レポートを生成."""
    if not report_input.tasks:
        raise HTTPException(status_code=400, detail="タスクリストが空です")
    report = generate_weekly_report(report_input)
    return report.model_dump(mode="json")


@app.post("/api/v1/vendors/evaluate")
def evaluate_vendors_endpoint(
    requirement: RFPRequirement,
    proposals: list[VendorProposal],
) -> dict[str, Any]:
    """ベンダー評価を実行."""
    if not proposals:
        raise HTTPException(status_code=400, detail="提案リストが空です")
    result = evaluate_vendors(requirement, proposals)
    return result.model_dump(mode="json")


@app.get("/api/v1/projects")
def list_projects() -> list[dict[str, Any]]:
    """プロジェクト一覧."""
    return db.list_projects()


@app.get("/api/v1/projects/{project_id}")
def get_project(project_id: int) -> dict[str, Any]:
    """プロジェクト詳細."""
    project = db.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="プロジェクトが見つかりません")
    return project
