"""プロジェクト計画AIサービス.

プロジェクト概要からWBS自動生成、PMBOK/Agileベースのフェーズ設計、
マイルストーン設定、ガントチャートデータ生成を行う。
"""

from __future__ import annotations

from app.knowledge.agile_framework import AgileFramework
from app.knowledge.pmbok_framework import PMBOKFramework
from app.models import (
    GanttItem,
    Methodology,
    Milestone,
    Phase,
    ProjectInput,
    ProjectPlan,
    WBSTask,
)
from app.services.wbs_generator import generate_wbs


def _apply_agile_overlay(
    phases: list[Phase],
    methodology: Methodology,
) -> list[Phase]:
    """アジャイル方法論に基づくフェーズ調整."""
    agile = AgileFramework()

    if methodology == Methodology.SCRUM:
        sprint_tasks = agile.get_recommended_sprint_tasks()
        # Scrumの場合、開発フェーズにスプリントイベントを追加
        for phase in phases:
            if "開発" in phase.name or "実装" in phase.name:
                phase.description += f" | Scrumイベント: {', '.join(sprint_tasks[:3])}"
    elif methodology == Methodology.KANBAN:
        practices = agile.kanban.get_practices_list()
        for phase in phases:
            phase.description += f" | Kanban: WIP制限={agile.kanban.default_wip_limit}"
    elif methodology == Methodology.SAFE:
        for phase in phases:
            phase.description += " | SAFe: PI Planning対象"

    return phases


def _apply_pmbok_governance(
    phases: list[Phase],
    milestones: list[Milestone],
) -> list[Phase]:
    """PMBOK原則に基づくガバナンス適用."""
    pmbok = PMBOKFramework()

    # 計画フェーズにPMBOKアクティビティを注釈
    planning_activities = pmbok.get_planning_activities()
    for phase in phases:
        if "計画" in phase.name or "要件" in phase.name:
            phase.description += (
                f" | PMBOK計画: {', '.join(planning_activities[:3])}"
            )

    return phases


def _scale_tasks_by_team_size(
    tasks: list[WBSTask],
    team_size: int,
) -> list[WBSTask]:
    """チーム規模に応じたタスク期間スケーリング.

    大きなチームでは並列作業が増えるため、実装系タスクの期間を短縮。
    ただし、コミュニケーションオーバーヘッドも考慮。
    """
    if team_size <= 3:
        return tasks

    # Brooks's Lawを考慮: 効率は人数に比例しない
    # 効率係数 = sqrt(team_size) / team_size * 調整係数
    # 小規模(~5): ほぼ線形 / 中規模(~15): 効率低下 / 大規模(30+): 大幅低下
    import math
    efficiency = min(1.0, math.sqrt(team_size) / team_size * 3.0)
    scale_factor = max(0.4, 1.0 - (1.0 - efficiency) * 0.5)

    result = []
    for task in tasks:
        if task.is_milestone:
            result.append(task)
        else:
            result.append(task.model_copy(update={
                "expected_days": round(task.expected_days * scale_factor, 1),
            }))
    return result


def create_project_plan(project_input: ProjectInput) -> ProjectPlan:
    """プロジェクト計画を作成.

    Args:
        project_input: プロジェクト概要入力

    Returns:
        完全なプロジェクト計画
    """
    # WBS生成
    wbs_result = generate_wbs(
        project_type=project_input.project_type,
        project_name=project_input.name,
        start_date=project_input.start_date,
    )

    tasks: list[WBSTask] = wbs_result["tasks"]
    milestones: list[Milestone] = wbs_result["milestones"]
    phases: list[Phase] = wbs_result["phases"]
    critical_path: list[str] = wbs_result["critical_path"]
    gantt_data: list[GanttItem] = wbs_result["gantt_data"]

    # チーム規模に応じたスケーリング
    tasks = _scale_tasks_by_team_size(tasks, project_input.team_size)

    # 方法論オーバーレイ
    phases = _apply_agile_overlay(phases, project_input.methodology)

    # PMBOKガバナンス
    phases = _apply_pmbok_governance(phases, milestones)

    # 合計見積もり日数を再計算
    total_days = sum(t.expected_days for t in tasks if not t.is_milestone)

    return ProjectPlan(
        project_name=project_input.name,
        project_type=project_input.project_type,
        methodology=project_input.methodology,
        phases=phases,
        tasks=tasks,
        milestones=milestones,
        critical_path=critical_path,
        total_estimated_days=round(total_days, 1),
        gantt_data=gantt_data,
    )


def get_project_summary(plan: ProjectPlan) -> dict[str, object]:
    """プロジェクト計画のサマリーを取得."""
    return {
        "project_name": plan.project_name,
        "project_type": plan.project_type.value,
        "methodology": plan.methodology.value,
        "total_tasks": len(plan.tasks),
        "milestones": len(plan.milestones),
        "critical_path_length": len(plan.critical_path),
        "total_estimated_days": plan.total_estimated_days,
        "phases": [p.name for p in plan.phases],
    }
