"""週次レポート自動生成サービス.

プロジェクト状況データから日英両言語の週次レポートを自動生成。
経営層サマリーと詳細版を含む。
"""

from __future__ import annotations

from datetime import date

from app.models import (
    EVMMetrics,
    RiskItem,
    TaskProgress,
    WeeklyReport,
    WeeklyReportInput,
)
from app.services.risk_analyzer import analyze_risks


def _task_status_summary(tasks: list[TaskProgress]) -> dict[str, int]:
    """タスクステータスの集計."""
    summary: dict[str, int] = {
        "completed": 0,
        "in_progress": 0,
        "not_started": 0,
        "delayed": 0,
        "blocked": 0,
    }
    for task in tasks:
        key = task.status.value
        summary[key] = summary.get(key, 0) + 1
    return summary


def _overall_progress(tasks: list[TaskProgress]) -> float:
    """全体進捗率計算."""
    if not tasks:
        return 0.0
    total = sum(t.percent_complete for t in tasks)
    return round(total / len(tasks), 4)


def _generate_executive_summary_ja(
    project_name: str,
    report_date: date,
    status_summary: dict[str, int],
    progress: float,
    evm: EVMMetrics | None,
    risks: list[RiskItem],
    health: str,
    highlights: list[str],
    issues: list[str],
) -> str:
    """経営層向け日本語サマリー生成."""
    total_tasks = sum(status_summary.values())
    critical_risks = [r for r in risks if r.level.value == "critical"]
    high_risks = [r for r in risks if r.level.value == "high"]

    health_ja = {
        "HEALTHY": "良好",
        "WARNING": "注意",
        "CRITICAL": "危険",
    }.get(health, health)

    lines = [
        f"# {project_name} 週次レポート",
        f"**報告日**: {report_date}",
        "",
        "## エグゼクティブサマリー",
        "",
        f"**プロジェクト健全性**: {health_ja}",
        f"**全体進捗**: {progress:.1%}",
        f"**タスク状況**: 完了 {status_summary['completed']}/{total_tasks}, "
        f"進行中 {status_summary['in_progress']}, "
        f"遅延 {status_summary['delayed']}, "
        f"ブロック {status_summary['blocked']}",
    ]

    if evm:
        lines.extend([
            "",
            "### EVM指標",
            f"- SPI (スケジュール効率): {evm.spi:.2f}",
            f"- CPI (コスト効率): {evm.cpi:.2f}",
            f"- EAC (完成時見積): {evm.eac:,.0f}",
        ])

    if critical_risks or high_risks:
        lines.extend([
            "",
            "### 主要リスク",
        ])
        for risk in critical_risks + high_risks:
            lines.append(f"- **[{risk.level.value.upper()}]** {risk.description}")

    if highlights:
        lines.extend(["", "### 今週のハイライト"])
        for h in highlights:
            lines.append(f"- {h}")

    if issues:
        lines.extend(["", "### 課題"])
        for issue in issues:
            lines.append(f"- {issue}")

    return "\n".join(lines)


def _generate_executive_summary_en(
    project_name: str,
    report_date: date,
    status_summary: dict[str, int],
    progress: float,
    evm: EVMMetrics | None,
    risks: list[RiskItem],
    health: str,
    highlights: list[str],
    issues: list[str],
) -> str:
    """経営層向け英語サマリー生成."""
    total_tasks = sum(status_summary.values())
    critical_risks = [r for r in risks if r.level.value == "critical"]
    high_risks = [r for r in risks if r.level.value == "high"]

    lines = [
        f"# {project_name} Weekly Report",
        f"**Date**: {report_date}",
        "",
        "## Executive Summary",
        "",
        f"**Project Health**: {health}",
        f"**Overall Progress**: {progress:.1%}",
        f"**Task Status**: Completed {status_summary['completed']}/{total_tasks}, "
        f"In Progress {status_summary['in_progress']}, "
        f"Delayed {status_summary['delayed']}, "
        f"Blocked {status_summary['blocked']}",
    ]

    if evm:
        lines.extend([
            "",
            "### EVM Metrics",
            f"- SPI (Schedule Performance): {evm.spi:.2f}",
            f"- CPI (Cost Performance): {evm.cpi:.2f}",
            f"- EAC (Estimate at Completion): {evm.eac:,.0f}",
        ])

    if critical_risks or high_risks:
        lines.extend(["", "### Key Risks"])
        for risk in critical_risks + high_risks:
            lines.append(f"- **[{risk.level.value.upper()}]** {risk.description}")

    if highlights:
        lines.extend(["", "### This Week's Highlights"])
        for h in highlights:
            lines.append(f"- {h}")

    if issues:
        lines.extend(["", "### Issues"])
        for issue in issues:
            lines.append(f"- {issue}")

    return "\n".join(lines)


def _generate_detailed_report_ja(
    project_name: str,
    report_date: date,
    tasks: list[TaskProgress],
    status_summary: dict[str, int],
    evm: EVMMetrics | None,
    risks: list[RiskItem],
    recommendations: list[str],
    next_week_plan: list[str],
) -> str:
    """詳細版日本語レポート生成."""
    lines = [
        f"# {project_name} 週次詳細レポート",
        f"**報告日**: {report_date}",
        "",
        "## 1. タスク詳細",
        "",
        "| タスク | ステータス | 進捗 | 計画コスト | 実績コスト |",
        "|--------|-----------|------|-----------|-----------|",
    ]

    for task in tasks:
        lines.append(
            f"| {task.task_name} | {task.status.value} | "
            f"{task.percent_complete:.0%} | "
            f"{task.planned_cost:,.0f} | {task.actual_cost:,.0f} |",
        )

    if evm:
        lines.extend([
            "",
            "## 2. EVM分析",
            "",
            f"- BAC (総予算): {evm.bac:,.0f}",
            f"- PV (計画価値): {evm.pv:,.0f}",
            f"- EV (出来高): {evm.ev:,.0f}",
            f"- AC (実績コスト): {evm.ac:,.0f}",
            f"- SV (スケジュール差異): {evm.sv:,.0f}",
            f"- CV (コスト差異): {evm.cv:,.0f}",
            f"- SPI: {evm.spi:.4f}",
            f"- CPI: {evm.cpi:.4f}",
            f"- EAC: {evm.eac:,.0f}",
            f"- ETC: {evm.etc:,.0f}",
            f"- VAC: {evm.vac:,.0f}",
            f"- TCPI: {evm.tcpi:.4f}",
        ])

    if risks:
        lines.extend(["", "## 3. リスクレジスタ", ""])
        for risk in risks:
            lines.append(
                f"- **[{risk.level.value.upper()}]** {risk.risk_id}: {risk.description}\n"
                f"  - 確率: {risk.probability:.0%} / 影響度: {risk.impact:.0%} / "
                f"スコア: {risk.risk_score:.2f}\n"
                f"  - 対策: {risk.mitigation}\n"
                f"  - 緊急時: {risk.contingency}",
            )

    if recommendations:
        lines.extend(["", "## 4. 推奨アクション", ""])
        for rec in recommendations:
            lines.append(f"- {rec}")

    if next_week_plan:
        lines.extend(["", "## 5. 来週の計画", ""])
        for plan in next_week_plan:
            lines.append(f"- {plan}")

    return "\n".join(lines)


def _generate_detailed_report_en(
    project_name: str,
    report_date: date,
    tasks: list[TaskProgress],
    status_summary: dict[str, int],
    evm: EVMMetrics | None,
    risks: list[RiskItem],
    recommendations: list[str],
    next_week_plan: list[str],
) -> str:
    """詳細版英語レポート生成."""
    lines = [
        f"# {project_name} Detailed Weekly Report",
        f"**Date**: {report_date}",
        "",
        "## 1. Task Details",
        "",
        "| Task | Status | Progress | Planned Cost | Actual Cost |",
        "|------|--------|----------|-------------|-------------|",
    ]

    for task in tasks:
        lines.append(
            f"| {task.task_name} | {task.status.value} | "
            f"{task.percent_complete:.0%} | "
            f"{task.planned_cost:,.0f} | {task.actual_cost:,.0f} |",
        )

    if evm:
        lines.extend([
            "",
            "## 2. EVM Analysis",
            "",
            f"- BAC: {evm.bac:,.0f}",
            f"- PV: {evm.pv:,.0f}",
            f"- EV: {evm.ev:,.0f}",
            f"- AC: {evm.ac:,.0f}",
            f"- SV: {evm.sv:,.0f}",
            f"- CV: {evm.cv:,.0f}",
            f"- SPI: {evm.spi:.4f}",
            f"- CPI: {evm.cpi:.4f}",
            f"- EAC: {evm.eac:,.0f}",
            f"- ETC: {evm.etc:,.0f}",
            f"- VAC: {evm.vac:,.0f}",
            f"- TCPI: {evm.tcpi:.4f}",
        ])

    if risks:
        lines.extend(["", "## 3. Risk Register", ""])
        for risk in risks:
            lines.append(
                f"- **[{risk.level.value.upper()}]** {risk.risk_id}: {risk.description}\n"
                f"  - Probability: {risk.probability:.0%} / Impact: {risk.impact:.0%} / "
                f"Score: {risk.risk_score:.2f}\n"
                f"  - Mitigation: {risk.mitigation}\n"
                f"  - Contingency: {risk.contingency}",
            )

    if recommendations:
        lines.extend(["", "## 4. Recommendations", ""])
        for rec in recommendations:
            lines.append(f"- {rec}")

    if next_week_plan:
        lines.extend(["", "## 5. Next Week Plan", ""])
        for plan in next_week_plan:
            lines.append(f"- {plan}")

    return "\n".join(lines)


def generate_weekly_report(report_input: WeeklyReportInput) -> WeeklyReport:
    """週次レポートを生成.

    Args:
        report_input: レポート入力データ

    Returns:
        日英両言語のレポート
    """
    # タスクステータス集計
    status_summary = _task_status_summary(report_input.tasks)
    progress = _overall_progress(report_input.tasks)

    # リスク分析
    risk_result = analyze_risks(report_input.tasks, report_input.report_date)
    evm = risk_result.evm
    risks = risk_result.risk_register
    health = risk_result.health_status
    recommendations = risk_result.recommendations

    # 日本語エグゼクティブサマリー
    exec_ja = _generate_executive_summary_ja(
        report_input.project_name,
        report_input.report_date,
        status_summary,
        progress,
        evm,
        risks,
        health,
        report_input.highlights,
        report_input.issues,
    )

    # 英語エグゼクティブサマリー
    exec_en = _generate_executive_summary_en(
        report_input.project_name,
        report_input.report_date,
        status_summary,
        progress,
        evm,
        risks,
        health,
        report_input.highlights,
        report_input.issues,
    )

    # 日本語詳細レポート
    detail_ja = _generate_detailed_report_ja(
        report_input.project_name,
        report_input.report_date,
        report_input.tasks,
        status_summary,
        evm,
        risks,
        recommendations,
        report_input.next_week_plan,
    )

    # 英語詳細レポート
    detail_en = _generate_detailed_report_en(
        report_input.project_name,
        report_input.report_date,
        report_input.tasks,
        status_summary,
        evm,
        risks,
        recommendations,
        report_input.next_week_plan,
    )

    # アクションアイテム抽出
    action_items = recommendations.copy()
    for issue in report_input.issues:
        action_items.append(f"課題対応: {issue}")

    return WeeklyReport(
        project_name=report_input.project_name,
        report_date=report_input.report_date,
        executive_summary_ja=exec_ja,
        executive_summary_en=exec_en,
        detailed_report_ja=detail_ja,
        detailed_report_en=detail_en,
        evm=evm,
        risks=risks,
        action_items=action_items,
    )
