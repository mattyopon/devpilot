"""WBS自動生成サービス.

プロジェクト種別テンプレートからWBSを生成。
タスク依存関係、3点見積もり、クリティカルパス計算を行う。
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from app.knowledge.project_templates import ALL_TEMPLATES, TemplateTask, get_template
from app.models import GanttItem, Milestone, Phase, ProjectType, WBSTask


def calculate_pert_estimate(
    optimistic: float,
    most_likely: float,
    pessimistic: float,
) -> float:
    """PERT 3点見積もり (O + 4M + P) / 6."""
    return (optimistic + 4 * most_likely + pessimistic) / 6


def _build_wbs_task(
    template_task: TemplateTask,
    task_prefix: str,
) -> WBSTask:
    """テンプレートタスクからWBSタスクを生成."""
    expected = calculate_pert_estimate(
        template_task.optimistic_days,
        template_task.most_likely_days,
        template_task.pessimistic_days,
    )
    return WBSTask(
        task_id=template_task.task_id,
        name=template_task.name,
        description=template_task.description,
        parent_id=template_task.parent_id,
        dependencies=list(template_task.dependencies),
        optimistic_days=template_task.optimistic_days,
        most_likely_days=template_task.most_likely_days,
        pessimistic_days=template_task.pessimistic_days,
        expected_days=round(expected, 1),
        assigned_role=template_task.assigned_role,
        is_milestone=template_task.is_milestone,
    )


def calculate_critical_path(tasks: list[WBSTask]) -> list[str]:
    """クリティカルパス計算 (最長パス法).

    タスクの依存関係グラフからクリティカルパス（最長パス）を算出する。
    """
    task_map: dict[str, WBSTask] = {t.task_id: t for t in tasks}

    # 各タスクの最早開始/終了時間を前方パスで計算
    earliest_start: dict[str, float] = {}
    earliest_finish: dict[str, float] = {}

    def _get_earliest_finish(task_id: str) -> float:
        if task_id in earliest_finish:
            return earliest_finish[task_id]
        task = task_map[task_id]
        if not task.dependencies:
            earliest_start[task_id] = 0
        else:
            earliest_start[task_id] = max(
                _get_earliest_finish(dep) for dep in task.dependencies
                if dep in task_map
            )
        earliest_finish[task_id] = earliest_start[task_id] + task.expected_days
        return earliest_finish[task_id]

    for task_id in task_map:
        _get_earliest_finish(task_id)

    if not earliest_finish:
        return []

    project_duration = max(earliest_finish.values())

    # 後方パスで最遅開始/終了時間を計算
    latest_finish: dict[str, float] = {}
    latest_start: dict[str, float] = {}

    # 後続タスクマップ
    successors: dict[str, list[str]] = {tid: [] for tid in task_map}
    for task in tasks:
        for dep in task.dependencies:
            if dep in successors:
                successors[dep].append(task.task_id)

    def _get_latest_start(task_id: str) -> float:
        if task_id in latest_start:
            return latest_start[task_id]
        task = task_map[task_id]
        if not successors[task_id]:
            latest_finish[task_id] = project_duration
        else:
            latest_finish[task_id] = min(
                _get_latest_start(succ) for succ in successors[task_id]
            )
        latest_start[task_id] = latest_finish[task_id] - task.expected_days
        return latest_start[task_id]

    for task_id in task_map:
        _get_latest_start(task_id)

    # フロート=0のタスクがクリティカルパス
    critical_tasks = [
        task_id
        for task_id in task_map
        if abs(latest_start.get(task_id, 0) - earliest_start.get(task_id, 0)) < 0.01
    ]

    # トポロジカル順序でソート
    return sorted(critical_tasks, key=lambda tid: earliest_start.get(tid, 0))


def schedule_tasks(
    tasks: list[WBSTask],
    start_date: date,
) -> list[WBSTask]:
    """タスクにスケジュール日付を割り当てる."""
    task_map: dict[str, WBSTask] = {t.task_id: t for t in tasks}
    scheduled: dict[str, date] = {}

    def _get_task_start(task_id: str) -> date:
        if task_id in scheduled:
            return scheduled[task_id]
        task = task_map[task_id]
        if not task.dependencies:
            scheduled[task_id] = start_date
            return start_date
        dep_end_dates = []
        for dep in task.dependencies:
            if dep in task_map:
                dep_start = _get_task_start(dep)
                dep_task = task_map[dep]
                dep_end = dep_start + timedelta(days=int(dep_task.expected_days))
                dep_end_dates.append(dep_end)
        task_start = max(dep_end_dates) if dep_end_dates else start_date
        scheduled[task_id] = task_start
        return task_start

    result = []
    for task in tasks:
        task_start = _get_task_start(task.task_id)
        task_end = task_start + timedelta(days=max(1, int(task.expected_days)))
        result.append(task.model_copy(update={
            "start_date": task_start,
            "end_date": task_end,
        }))

    return result


def generate_gantt_data(tasks: list[WBSTask]) -> list[GanttItem]:
    """ガントチャートデータを生成."""
    return [
        GanttItem(
            task_id=task.task_id,
            task_name=task.name,
            start_date=task.start_date or date.today(),
            end_date=task.end_date or date.today(),
            progress=0.0,
            dependencies=task.dependencies,
            is_critical=task.is_critical_path,
        )
        for task in tasks
        if not task.is_milestone
    ]


def extract_milestones(tasks: list[WBSTask]) -> list[Milestone]:
    """マイルストーンを抽出."""
    return [
        Milestone(
            milestone_id=task.task_id,
            name=task.name,
            target_date=task.end_date or task.start_date or date.today(),
            deliverables=[task.description],
            criteria=[f"{task.name}完了"],
        )
        for task in tasks
        if task.is_milestone
    ]


def generate_wbs(
    project_type: ProjectType,
    project_name: str,
    start_date: date,
) -> dict[str, Any]:
    """WBSを生成.

    Args:
        project_type: プロジェクト種別
        project_name: プロジェクト名
        start_date: 開始日

    Returns:
        WBS生成結果 (tasks, milestones, critical_path, phases, gantt_data, total_days)
    """
    template = get_template(project_type.value)
    if template is None:
        # デフォルトでWeb開発テンプレートを使用
        template = ALL_TEMPLATES["web_development"]

    # テンプレートからWBSタスクを生成
    tasks = [_build_wbs_task(tt, project_name) for tt in template.tasks]

    # クリティカルパス計算
    critical_path = calculate_critical_path(tasks)

    # クリティカルパスフラグ設定
    for task in tasks:
        if task.task_id in critical_path:
            task.is_critical_path = True

    # スケジューリング
    tasks = schedule_tasks(tasks, start_date)

    # マイルストーン抽出
    milestones = extract_milestones(tasks)

    # ガントチャートデータ
    gantt_data = generate_gantt_data(tasks)

    # フェーズ生成
    phases = [
        Phase(
            phase_id=f"PH{i+1:02d}",
            name=phase_name,
            description=f"{phase_name}フェーズ",
            order=i + 1,
            task_ids=[],  # 簡略化
        )
        for i, phase_name in enumerate(template.phases)
    ]

    # 合計見積もり日数
    total_days = sum(t.expected_days for t in tasks if not t.is_milestone)

    return {
        "tasks": tasks,
        "milestones": milestones,
        "critical_path": critical_path,
        "phases": phases,
        "gantt_data": gantt_data,
        "total_estimated_days": round(total_days, 1),
        "template_name": template.name,
        "recommended_roles": list(template.recommended_team_roles),
    }
