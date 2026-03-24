"""リスク分析AIサービス.

タスク進捗データから遅延リスク予測、EVM指標自動計算、
リスクレジスタ生成、リスク対応策提案を行う。
"""

from __future__ import annotations

from datetime import date

from app.knowledge.evm_formulas import (
    EVMInput,
    calculate_evm,
    interpret_cpi,
    interpret_health,
    interpret_spi,
)
from app.models import (
    EVMMetrics,
    RiskAnalysisResult,
    RiskItem,
    RiskLevel,
    TaskProgress,
    TaskStatus,
)


def _calculate_evm_from_tasks(
    tasks: list[TaskProgress],
    reference_date: date | None = None,
) -> EVMMetrics:
    """タスク進捗データからEVM指標を計算."""
    if reference_date is None:
        reference_date = date.today()

    bac = sum(t.planned_cost for t in tasks)
    ac = sum(t.actual_cost for t in tasks)

    # EV: 各タスクの計画コスト × 完了率
    ev = sum(t.planned_cost * t.percent_complete for t in tasks)

    # PV: 期日までに完了すべき計画値
    pv = 0.0
    for task in tasks:
        if task.planned_end <= reference_date:
            pv += task.planned_cost
        elif task.planned_start <= reference_date:
            total_days = (task.planned_end - task.planned_start).days
            elapsed_days = (reference_date - task.planned_start).days
            if total_days > 0:
                ratio = min(1.0, elapsed_days / total_days)
                pv += task.planned_cost * ratio
            else:
                pv += task.planned_cost

    evm_input = EVMInput(bac=bac, pv=pv, ev=ev, ac=ac)
    result = calculate_evm(evm_input)

    return EVMMetrics(
        bac=result.bac,
        pv=round(result.pv, 2),
        ev=round(result.ev, 2),
        ac=round(result.ac, 2),
        sv=round(result.sv, 2),
        cv=round(result.cv, 2),
        spi=round(result.spi, 4),
        cpi=round(result.cpi, 4),
        eac=round(result.eac, 2),
        etc=round(result.etc, 2),
        vac=round(result.vac, 2),
        tcpi=round(result.tcpi, 4),
    )


def _identify_delayed_tasks(tasks: list[TaskProgress]) -> list[TaskProgress]:
    """遅延タスクの特定."""
    today = date.today()
    delayed = []
    for task in tasks:
        if task.status == TaskStatus.COMPLETED:
            continue
        if task.planned_end < today and task.percent_complete < 1.0:
            delayed.append(task)
        elif task.planned_start < today and task.percent_complete < 0.1:
            delayed.append(task)
    return delayed


def _calculate_delay_probability(
    evm: EVMMetrics,
    tasks: list[TaskProgress],
) -> float:
    """遅延確率の推定.

    SPI、遅延タスク数、進捗率に基づくヒューリスティック計算。
    """
    delayed = _identify_delayed_tasks(tasks)
    delay_ratio = len(delayed) / max(len(tasks), 1)

    # SPIベースの遅延確率
    if evm.spi >= 1.0:
        spi_factor = 0.0
    elif evm.spi >= 0.9:
        spi_factor = 0.2
    elif evm.spi >= 0.8:
        spi_factor = 0.5
    else:
        spi_factor = 0.8

    probability = min(1.0, spi_factor * 0.6 + delay_ratio * 0.4)
    return round(probability, 2)


def _calculate_budget_overrun_probability(evm: EVMMetrics) -> float:
    """予算超過確率の推定."""
    if evm.cpi >= 1.0:
        return 0.0
    if evm.cpi >= 0.9:
        return round(0.3 * (1.0 - evm.cpi) / 0.1, 2)
    if evm.cpi >= 0.8:
        return round(0.3 + 0.3 * (0.9 - evm.cpi) / 0.1, 2)
    return min(1.0, round(0.6 + 0.4 * (0.8 - evm.cpi) / 0.2, 2))


def _generate_risk_register(
    evm: EVMMetrics,
    tasks: list[TaskProgress],
) -> list[RiskItem]:
    """リスクレジスタ生成."""
    risks: list[RiskItem] = []
    risk_counter = 1

    # スケジュールリスク
    if evm.spi < 1.0:
        severity = 1.0 - evm.spi
        level = (
            RiskLevel.CRITICAL if severity > 0.2
            else RiskLevel.HIGH if severity > 0.1
            else RiskLevel.MEDIUM
        )
        risks.append(RiskItem(
            risk_id=f"R{risk_counter:03d}",
            category="スケジュール",
            description=f"SPI={evm.spi:.2f} スケジュール遅延リスク。{interpret_spi(evm.spi)}",
            probability=min(1.0, severity * 2),
            impact=min(1.0, severity * 2.5),
            risk_score=round(min(1.0, severity * 2) * min(1.0, severity * 2.5), 2),
            level=level,
            mitigation="クリティカルパスタスクへのリソース増強、スコープ見直し",
            contingency="スケジュール再ベースライン、ステークホルダーへの遅延報告",
        ))
        risk_counter += 1

    # コストリスク
    if evm.cpi < 1.0:
        severity = 1.0 - evm.cpi
        level = (
            RiskLevel.CRITICAL if severity > 0.2
            else RiskLevel.HIGH if severity > 0.1
            else RiskLevel.MEDIUM
        )
        risks.append(RiskItem(
            risk_id=f"R{risk_counter:03d}",
            category="コスト",
            description=f"CPI={evm.cpi:.2f} 予算超過リスク。{interpret_cpi(evm.cpi)}",
            probability=min(1.0, severity * 2),
            impact=min(1.0, severity * 2.5),
            risk_score=round(min(1.0, severity * 2) * min(1.0, severity * 2.5), 2),
            level=level,
            mitigation="コスト構造の見直し、低優先度タスクの削減",
            contingency="予備費の活用、スコープ縮小の検討",
        ))
        risk_counter += 1

    # 遅延タスクリスク
    delayed = _identify_delayed_tasks(tasks)
    if delayed:
        for task in delayed[:5]:  # 上位5件
            risks.append(RiskItem(
                risk_id=f"R{risk_counter:03d}",
                category="タスク遅延",
                description=f"タスク '{task.task_name}' が遅延中 (進捗: {task.percent_complete:.0%})",
                probability=0.8,
                impact=0.6,
                risk_score=0.48,
                level=RiskLevel.HIGH,
                mitigation=f"'{task.task_name}' へのリソース追加投入",
                contingency="タスク分割・並列化、担当変更",
            ))
            risk_counter += 1

    # リソースリスク（共通）
    blocked_tasks = [t for t in tasks if t.status == TaskStatus.BLOCKED]
    if blocked_tasks:
        risks.append(RiskItem(
            risk_id=f"R{risk_counter:03d}",
            category="リソース/ブロッカー",
            description=f"{len(blocked_tasks)}件のタスクがブロック状態",
            probability=0.9,
            impact=0.7,
            risk_score=0.63,
            level=RiskLevel.HIGH,
            mitigation="ブロッカーの根本原因分析と除去",
            contingency="代替アプローチの検討、エスカレーション",
        ))
        risk_counter += 1

    return risks


def _generate_recommendations(
    evm: EVMMetrics,
    risks: list[RiskItem],
    tasks: list[TaskProgress],
) -> list[str]:
    """推奨アクション生成."""
    recommendations: list[str] = []

    if evm.spi < 0.9:
        recommendations.append(
            "【緊急】スケジュール遅延が深刻です。クリティカルパスの見直しと"
            "リソース再配分を直ちに実施してください。"
        )
    elif evm.spi < 1.0:
        recommendations.append(
            "スケジュールに遅延傾向があります。週次での進捗モニタリングを強化してください。"
        )

    if evm.cpi < 0.9:
        recommendations.append(
            "【緊急】予算超過が深刻です。コスト構造の見直しとスコープ調整を検討してください。"
        )
    elif evm.cpi < 1.0:
        recommendations.append(
            "コスト効率に改善の余地があります。無駄なコストの削減を検討してください。"
        )

    if evm.tcpi > 1.2:
        recommendations.append(
            "残作業の効率指数(TCPI)が高すぎます。"
            "現在のペースでは予算内完了が困難な可能性があります。"
        )

    critical_risks = [r for r in risks if r.level == RiskLevel.CRITICAL]
    if critical_risks:
        recommendations.append(
            f"クリティカルリスクが{len(critical_risks)}件あります。"
            "リスク対応会議の実施を推奨します。"
        )

    not_started = [t for t in tasks if t.status == TaskStatus.NOT_STARTED]
    if len(not_started) > len(tasks) * 0.5:
        recommendations.append(
            "未着手タスクが全体の50%を超えています。計画の見直しを検討してください。"
        )

    if not recommendations:
        recommendations.append(
            "プロジェクトは順調に進行しています。現在の方針を継続してください。"
        )

    return recommendations


def analyze_risks(
    tasks: list[TaskProgress],
    reference_date: date | None = None,
) -> RiskAnalysisResult:
    """リスク分析を実行.

    Args:
        tasks: タスク進捗データリスト
        reference_date: 基準日（デフォルト: 今日）

    Returns:
        リスク分析結果
    """
    evm = _calculate_evm_from_tasks(tasks, reference_date)
    risk_register = _generate_risk_register(evm, tasks)
    delay_prob = _calculate_delay_probability(evm, tasks)
    budget_prob = _calculate_budget_overrun_probability(evm)
    health = interpret_health(evm.spi, evm.cpi)
    recommendations = _generate_recommendations(evm, risk_register, tasks)

    return RiskAnalysisResult(
        evm=evm,
        risk_register=risk_register,
        delay_probability=delay_prob,
        budget_overrun_probability=budget_prob,
        recommendations=recommendations,
        health_status=health,
    )
