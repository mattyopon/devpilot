"""ベンダー評価AIサービス.

RFPテンプレート生成、提案比較マトリクス、TCO比較を行う。
"""

from __future__ import annotations

from app.models import (
    ProjectType,
    RFPRequirement,
    VendorEvaluationResult,
    VendorProposal,
    VendorScore,
)


def _generate_rfp_template(requirement: RFPRequirement) -> str:
    """RFPテンプレート生成."""
    project_type_ja = {
        ProjectType.WEB_DEV: "Webアプリケーション開発",
        ProjectType.INFRASTRUCTURE: "インフラ構築",
        ProjectType.ERP: "ERP導入",
        ProjectType.MOBILE: "モバイルアプリ開発",
        ProjectType.AI_ML: "AI/ML開発",
    }.get(requirement.project_type, requirement.project_type.value)

    budget_section = ""
    if requirement.budget_range_jpy:
        low, high = requirement.budget_range_jpy
        budget_section = f"""
## 5. 予算
- 想定予算範囲: {low:,}円 〜 {high:,}円（税別）
- 上記はあくまで目安であり、提案内容に応じて柔軟に検討します
"""

    eval_criteria = requirement.evaluation_criteria or [
        "技術力・実績",
        "コスト",
        "スケジュール",
        "サポート体制",
        "提案の理解度",
    ]

    eval_section = "\n".join(f"- {c}" for c in eval_criteria)

    req_section = "\n".join(f"- {r}" for r in requirement.requirements)

    return f"""# 提案依頼書 (RFP)

## 1. プロジェクト概要
- **プロジェクト名**: {requirement.project_name}
- **種別**: {project_type_ja}
- **スコープ**: {requirement.scope}
- **期間**: {requirement.timeline_months}ヶ月

## 2. 要件
{req_section}

## 3. 提出物
- 提案書（技術提案・体制・スケジュール・費用見積もり）
- 会社概要・実績一覧
- 参考顧客リスト
- SLA提案

## 4. 評価基準
{eval_section}
{budget_section}
## 6. スケジュール
- RFP発行: [日付]
- 質問受付期限: [日付]
- 提案書提出期限: [日付]
- プレゼンテーション: [日付]
- ベンダー選定: [日付]

## 7. 提出先・問い合わせ先
- 担当者名: [担当者]
- メール: [メールアドレス]
- 電話: [電話番号]
"""


def _calculate_tco_5year(proposal: VendorProposal) -> float:
    """5年間TCO計算."""
    return proposal.initial_cost + proposal.annual_maintenance_cost * 5


def _score_cost(
    proposal: VendorProposal,
    all_proposals: list[VendorProposal],
) -> float:
    """コストスコア計算 (TCOが最も低い提案が10点)."""
    tcos = [_calculate_tco_5year(p) for p in all_proposals]
    min_tco = min(tcos) if tcos else 1
    max_tco = max(tcos) if tcos else 1
    if max_tco == min_tco:
        return 8.0
    my_tco = _calculate_tco_5year(proposal)
    # 最小TCOが10点、最大が2点
    score = 10.0 - 8.0 * (my_tco - min_tco) / (max_tco - min_tco)
    return round(max(2.0, min(10.0, score)), 1)


def _score_technical(proposal: VendorProposal) -> float:
    """技術スコア計算."""
    base_score = 5.0
    # 技術スタック数で加点
    tech_count = len(proposal.technology_stack)
    base_score += min(3.0, tech_count * 0.5)
    # SLAで加点
    if proposal.sla_uptime >= 99.9:
        base_score += 1.5
    elif proposal.sla_uptime >= 99.5:
        base_score += 1.0
    elif proposal.sla_uptime >= 99.0:
        base_score += 0.5
    return round(min(10.0, base_score), 1)


def _score_experience(proposal: VendorProposal) -> float:
    """実績スコア計算."""
    base_score = 5.0
    # 参考顧客数で加点
    base_score += min(3.0, proposal.references * 0.5)
    # チーム規模で加点（適正規模は3-15名）
    if 3 <= proposal.team_size <= 15:
        base_score += 1.0
    elif proposal.team_size > 15:
        base_score += 0.5
    return round(min(10.0, base_score), 1)


def _score_timeline(
    proposal: VendorProposal,
    all_proposals: list[VendorProposal],
) -> float:
    """タイムラインスコア計算."""
    months = [p.implementation_months for p in all_proposals]
    min_months = min(months) if months else 1
    max_months = max(months) if months else 1
    if max_months == min_months:
        return 8.0
    score = 10.0 - 8.0 * (proposal.implementation_months - min_months) / (max_months - min_months)
    return round(max(2.0, min(10.0, score)), 1)


def _score_support(proposal: VendorProposal) -> float:
    """サポートスコア計算."""
    base_score = 5.0
    if proposal.support_hours == "24x7":
        base_score += 4.0
    elif proposal.support_hours == "24x5":
        base_score += 3.0
    elif proposal.support_hours == "9x7":
        base_score += 2.0
    elif proposal.support_hours == "9x5":
        base_score += 1.0
    # SLA加点
    if proposal.sla_uptime >= 99.9:
        base_score += 1.0
    return round(min(10.0, base_score), 1)


def _identify_strengths_weaknesses(
    score: VendorScore,
) -> tuple[list[str], list[str]]:
    """強み・弱みの特定."""
    strengths: list[str] = []
    weaknesses: list[str] = []

    scores = {
        "コスト": score.cost_score,
        "技術力": score.technical_score,
        "実績": score.experience_score,
        "スケジュール": score.timeline_score,
        "サポート": score.support_score,
    }

    for name, value in scores.items():
        if value >= 8.0:
            strengths.append(f"{name}が優れている ({value}/10)")
        elif value <= 4.0:
            weaknesses.append(f"{name}に懸念 ({value}/10)")

    if not strengths:
        strengths.append("バランスの取れた提案")
    if not weaknesses:
        weaknesses.append("特になし")

    return strengths, weaknesses


def evaluate_vendors(
    requirement: RFPRequirement,
    proposals: list[VendorProposal],
) -> VendorEvaluationResult:
    """ベンダー評価を実行.

    Args:
        requirement: RFP要件
        proposals: ベンダー提案リスト

    Returns:
        ベンダー評価結果（RFP、スコア、比較マトリクス、TCO比較）
    """
    # RFPテンプレート生成
    rfp = _generate_rfp_template(requirement)

    # 各ベンダーのスコア計算
    scores: list[VendorScore] = []
    for proposal in proposals:
        cost_s = _score_cost(proposal, proposals)
        tech_s = _score_technical(proposal)
        exp_s = _score_experience(proposal)
        time_s = _score_timeline(proposal, proposals)
        sup_s = _score_support(proposal)

        # 重み付き合計 (コスト25%, 技術30%, 実績15%, 期間15%, サポート15%)
        total = round(
            cost_s * 0.25
            + tech_s * 0.30
            + exp_s * 0.15
            + time_s * 0.15
            + sup_s * 0.15,
            1,
        )

        tco = _calculate_tco_5year(proposal)

        vendor_score = VendorScore(
            vendor_name=proposal.vendor_name,
            cost_score=cost_s,
            technical_score=tech_s,
            experience_score=exp_s,
            timeline_score=time_s,
            support_score=sup_s,
            total_score=total,
            tco_5year=tco,
            strengths=[],
            weaknesses=[],
            recommendation="",
        )

        strengths, weaknesses = _identify_strengths_weaknesses(vendor_score)
        vendor_score = vendor_score.model_copy(update={
            "strengths": strengths,
            "weaknesses": weaknesses,
        })

        scores.append(vendor_score)

    # スコア順にソート
    scores.sort(key=lambda s: s.total_score, reverse=True)

    # 推奨ベンダー設定
    if scores:
        scores[0] = scores[0].model_copy(update={"recommendation": "最推奨"})
        if len(scores) > 1:
            scores[1] = scores[1].model_copy(update={"recommendation": "次点"})
        for i in range(2, len(scores)):
            scores[i] = scores[i].model_copy(update={"recommendation": "検討"})

    # 比較マトリクス
    comparison_matrix: dict[str, dict[str, float]] = {}
    for s in scores:
        comparison_matrix[s.vendor_name] = {
            "cost": s.cost_score,
            "technical": s.technical_score,
            "experience": s.experience_score,
            "timeline": s.timeline_score,
            "support": s.support_score,
            "total": s.total_score,
        }

    # TCO比較
    tco_comparison: dict[str, float] = {
        s.vendor_name: s.tco_5year for s in scores
    }

    # 全体推奨コメント
    recommendation = ""
    if scores:
        best = scores[0]
        recommendation = (
            f"総合評価の結果、{best.vendor_name}を最推奨します "
            f"(総合スコア: {best.total_score}/10, 5年TCO: {best.tco_5year:,.0f}円)。"
        )
        if len(scores) > 1:
            second = scores[1]
            recommendation += (
                f" 次点として{second.vendor_name}"
                f" (スコア: {second.total_score}/10) も検討に値します。"
            )

    return VendorEvaluationResult(
        rfp_template=rfp,
        scores=scores,
        comparison_matrix=comparison_matrix,
        recommendation=recommendation,
        tco_comparison=tco_comparison,
    )
