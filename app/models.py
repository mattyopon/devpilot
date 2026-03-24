"""DevPilot data models."""

from __future__ import annotations

import enum
from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


# --- Enums ---

class ProjectType(str, enum.Enum):
    """プロジェクト種別."""

    WEB_DEV = "web_development"
    INFRASTRUCTURE = "infrastructure"
    ERP = "erp_implementation"
    MOBILE = "mobile_app"
    AI_ML = "ai_ml"


class RiskLevel(str, enum.Enum):
    """リスクレベル."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskStatus(str, enum.Enum):
    """タスクステータス."""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DELAYED = "delayed"
    BLOCKED = "blocked"


class Methodology(str, enum.Enum):
    """プロジェクト方法論."""

    WATERFALL = "waterfall"
    SCRUM = "scrum"
    KANBAN = "kanban"
    SAFE = "safe"
    HYBRID = "hybrid"


# --- Project Planning ---

class ProjectInput(BaseModel):
    """プロジェクト概要入力."""

    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    project_type: ProjectType
    methodology: Methodology = Methodology.SCRUM
    start_date: date
    target_end_date: date
    team_size: int = Field(ge=1, le=500)
    budget_jpy: Optional[int] = Field(default=None, ge=0)


class WBSTask(BaseModel):
    """WBSタスク."""

    task_id: str
    name: str
    description: str
    parent_id: Optional[str] = None
    dependencies: list[str] = Field(default_factory=list)
    optimistic_days: float = Field(ge=0)
    most_likely_days: float = Field(ge=0)
    pessimistic_days: float = Field(ge=0)
    expected_days: float = Field(ge=0)
    assigned_role: Optional[str] = None
    status: TaskStatus = TaskStatus.NOT_STARTED
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_milestone: bool = False
    is_critical_path: bool = False


class Milestone(BaseModel):
    """マイルストーン."""

    milestone_id: str
    name: str
    target_date: date
    deliverables: list[str]
    criteria: list[str]


class ProjectPlan(BaseModel):
    """プロジェクト計画."""

    project_name: str
    project_type: ProjectType
    methodology: Methodology
    phases: list[Phase]
    tasks: list[WBSTask]
    milestones: list[Milestone]
    critical_path: list[str]
    total_estimated_days: float
    gantt_data: list[GanttItem]


class Phase(BaseModel):
    """プロジェクトフェーズ."""

    phase_id: str
    name: str
    description: str
    order: int
    task_ids: list[str]


class GanttItem(BaseModel):
    """ガントチャートデータ項目."""

    task_id: str
    task_name: str
    start_date: date
    end_date: date
    progress: float = Field(ge=0.0, le=1.0, default=0.0)
    dependencies: list[str] = Field(default_factory=list)
    is_critical: bool = False


# --- Risk Analysis ---

class TaskProgress(BaseModel):
    """タスク進捗データ."""

    task_id: str
    task_name: str
    planned_start: date
    planned_end: date
    actual_start: Optional[date] = None
    actual_end: Optional[date] = None
    planned_cost: float = Field(ge=0)
    actual_cost: float = Field(ge=0, default=0.0)
    percent_complete: float = Field(ge=0.0, le=1.0, default=0.0)
    status: TaskStatus = TaskStatus.NOT_STARTED


class EVMMetrics(BaseModel):
    """EVM指標."""

    bac: float = Field(ge=0, description="Budget at Completion")
    pv: float = Field(ge=0, description="Planned Value")
    ev: float = Field(ge=0, description="Earned Value")
    ac: float = Field(ge=0, description="Actual Cost")
    sv: float = Field(description="Schedule Variance (EV - PV)")
    cv: float = Field(description="Cost Variance (EV - AC)")
    spi: float = Field(description="Schedule Performance Index (EV / PV)")
    cpi: float = Field(description="Cost Performance Index (EV / AC)")
    eac: float = Field(description="Estimate at Completion (BAC / CPI)")
    etc: float = Field(description="Estimate to Complete (EAC - AC)")
    vac: float = Field(description="Variance at Completion (BAC - EAC)")
    tcpi: float = Field(description="To-Complete Performance Index")


class RiskItem(BaseModel):
    """リスク項目."""

    risk_id: str
    category: str
    description: str
    probability: float = Field(ge=0.0, le=1.0)
    impact: float = Field(ge=0.0, le=1.0)
    risk_score: float = Field(ge=0.0, le=1.0)
    level: RiskLevel
    mitigation: str
    contingency: str
    owner: Optional[str] = None


class RiskAnalysisResult(BaseModel):
    """リスク分析結果."""

    evm: EVMMetrics
    risk_register: list[RiskItem]
    delay_probability: float = Field(ge=0.0, le=1.0)
    budget_overrun_probability: float = Field(ge=0.0, le=1.0)
    recommendations: list[str]
    health_status: str


# --- Report ---

class WeeklyReportInput(BaseModel):
    """週次レポート入力."""

    project_name: str
    report_date: date
    tasks: list[TaskProgress]
    highlights: list[str] = Field(default_factory=list)
    issues: list[str] = Field(default_factory=list)
    next_week_plan: list[str] = Field(default_factory=list)


class WeeklyReport(BaseModel):
    """週次レポート."""

    project_name: str
    report_date: date
    executive_summary_ja: str
    executive_summary_en: str
    detailed_report_ja: str
    detailed_report_en: str
    evm: Optional[EVMMetrics] = None
    risks: list[RiskItem]
    action_items: list[str]


# --- Vendor Evaluation ---

class VendorProposal(BaseModel):
    """ベンダー提案."""

    vendor_name: str
    proposal_summary: str
    initial_cost: float = Field(ge=0)
    annual_maintenance_cost: float = Field(ge=0)
    implementation_months: int = Field(ge=1)
    team_size: int = Field(ge=1)
    technology_stack: list[str]
    references: int = Field(ge=0, default=0)
    sla_uptime: float = Field(ge=0.0, le=100.0, default=99.0)
    support_hours: str = "9x5"


class VendorScore(BaseModel):
    """ベンダー評価スコア."""

    vendor_name: str
    cost_score: float = Field(ge=0.0, le=10.0)
    technical_score: float = Field(ge=0.0, le=10.0)
    experience_score: float = Field(ge=0.0, le=10.0)
    timeline_score: float = Field(ge=0.0, le=10.0)
    support_score: float = Field(ge=0.0, le=10.0)
    total_score: float = Field(ge=0.0, le=10.0)
    tco_5year: float = Field(ge=0)
    strengths: list[str]
    weaknesses: list[str]
    recommendation: str


class VendorEvaluationResult(BaseModel):
    """ベンダー評価結果."""

    rfp_template: str
    scores: list[VendorScore]
    comparison_matrix: dict[str, dict[str, float]]
    recommendation: str
    tco_comparison: dict[str, float]


class RFPRequirement(BaseModel):
    """RFP要件."""

    project_name: str
    project_type: ProjectType
    scope: str
    requirements: list[str]
    budget_range_jpy: Optional[tuple[int, int]] = None
    timeline_months: int = Field(ge=1)
    evaluation_criteria: list[str] = Field(default_factory=list)
