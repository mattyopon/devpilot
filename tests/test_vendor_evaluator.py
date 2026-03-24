"""ベンダー評価AIサービスのテスト."""

from __future__ import annotations

import pytest

from app.models import ProjectType, RFPRequirement, VendorProposal
from app.services.vendor_evaluator import evaluate_vendors


@pytest.fixture()
def sample_requirement() -> RFPRequirement:
    """サンプルRFP要件."""
    return RFPRequirement(
        project_name="テストプロジェクト",
        project_type=ProjectType.WEB_DEV,
        scope="Webアプリケーション開発",
        requirements=["要件1", "要件2", "要件3"],
        budget_range_jpy=(10000000, 50000000),
        timeline_months=6,
        evaluation_criteria=["技術力", "コスト", "実績"],
    )


@pytest.fixture()
def sample_proposals() -> list[VendorProposal]:
    """サンプルベンダー提案."""
    return [
        VendorProposal(
            vendor_name="VendorA",
            proposal_summary="高品質提案",
            initial_cost=30000000,
            annual_maintenance_cost=5000000,
            implementation_months=5,
            team_size=10,
            technology_stack=["React", "Python", "PostgreSQL", "AWS"],
            references=5,
            sla_uptime=99.9,
            support_hours="24x7",
        ),
        VendorProposal(
            vendor_name="VendorB",
            proposal_summary="コスト重視提案",
            initial_cost=15000000,
            annual_maintenance_cost=3000000,
            implementation_months=8,
            team_size=5,
            technology_stack=["Vue.js", "Java"],
            references=2,
            sla_uptime=99.0,
            support_hours="9x5",
        ),
        VendorProposal(
            vendor_name="VendorC",
            proposal_summary="バランス提案",
            initial_cost=20000000,
            annual_maintenance_cost=4000000,
            implementation_months=6,
            team_size=7,
            technology_stack=["Angular", "Node.js", "MongoDB"],
            references=3,
            sla_uptime=99.5,
            support_hours="24x5",
        ),
    ]


class TestEvaluateVendors:
    """evaluate_vendors のテスト."""

    def test_generates_rfp_template(
        self,
        sample_requirement: RFPRequirement,
        sample_proposals: list[VendorProposal],
    ) -> None:
        result = evaluate_vendors(sample_requirement, sample_proposals)
        assert "提案依頼書" in result.rfp_template
        assert "テストプロジェクト" in result.rfp_template

    def test_rfp_includes_requirements(
        self,
        sample_requirement: RFPRequirement,
        sample_proposals: list[VendorProposal],
    ) -> None:
        result = evaluate_vendors(sample_requirement, sample_proposals)
        assert "要件1" in result.rfp_template

    def test_rfp_includes_budget(
        self,
        sample_requirement: RFPRequirement,
        sample_proposals: list[VendorProposal],
    ) -> None:
        result = evaluate_vendors(sample_requirement, sample_proposals)
        assert "予算" in result.rfp_template

    def test_scores_all_vendors(
        self,
        sample_requirement: RFPRequirement,
        sample_proposals: list[VendorProposal],
    ) -> None:
        result = evaluate_vendors(sample_requirement, sample_proposals)
        assert len(result.scores) == 3

    def test_scores_sorted_by_total(
        self,
        sample_requirement: RFPRequirement,
        sample_proposals: list[VendorProposal],
    ) -> None:
        result = evaluate_vendors(sample_requirement, sample_proposals)
        totals = [s.total_score for s in result.scores]
        assert totals == sorted(totals, reverse=True)

    def test_best_vendor_recommended(
        self,
        sample_requirement: RFPRequirement,
        sample_proposals: list[VendorProposal],
    ) -> None:
        result = evaluate_vendors(sample_requirement, sample_proposals)
        assert result.scores[0].recommendation == "最推奨"

    def test_second_vendor_is_runner_up(
        self,
        sample_requirement: RFPRequirement,
        sample_proposals: list[VendorProposal],
    ) -> None:
        result = evaluate_vendors(sample_requirement, sample_proposals)
        assert result.scores[1].recommendation == "次点"

    def test_comparison_matrix_complete(
        self,
        sample_requirement: RFPRequirement,
        sample_proposals: list[VendorProposal],
    ) -> None:
        result = evaluate_vendors(sample_requirement, sample_proposals)
        assert len(result.comparison_matrix) == 3
        for vendor_scores in result.comparison_matrix.values():
            assert "total" in vendor_scores
            assert "cost" in vendor_scores
            assert "technical" in vendor_scores

    def test_tco_comparison(
        self,
        sample_requirement: RFPRequirement,
        sample_proposals: list[VendorProposal],
    ) -> None:
        result = evaluate_vendors(sample_requirement, sample_proposals)
        assert len(result.tco_comparison) == 3
        # VendorBが最もTCOが低いはず (15M + 3M*5 = 30M)
        vendor_b_tco = result.tco_comparison["VendorB"]
        assert vendor_b_tco == 30000000

    def test_tco_calculation(
        self,
        sample_requirement: RFPRequirement,
        sample_proposals: list[VendorProposal],
    ) -> None:
        result = evaluate_vendors(sample_requirement, sample_proposals)
        # VendorA: 30M + 5M*5 = 55M
        assert result.tco_comparison["VendorA"] == 55000000
        # VendorC: 20M + 4M*5 = 40M
        assert result.tco_comparison["VendorC"] == 40000000

    def test_scores_in_valid_range(
        self,
        sample_requirement: RFPRequirement,
        sample_proposals: list[VendorProposal],
    ) -> None:
        result = evaluate_vendors(sample_requirement, sample_proposals)
        for score in result.scores:
            assert 0 <= score.cost_score <= 10
            assert 0 <= score.technical_score <= 10
            assert 0 <= score.experience_score <= 10
            assert 0 <= score.timeline_score <= 10
            assert 0 <= score.support_score <= 10
            assert 0 <= score.total_score <= 10

    def test_recommendation_text(
        self,
        sample_requirement: RFPRequirement,
        sample_proposals: list[VendorProposal],
    ) -> None:
        result = evaluate_vendors(sample_requirement, sample_proposals)
        assert "最推奨" in result.recommendation

    def test_single_vendor(self, sample_requirement: RFPRequirement) -> None:
        """単一ベンダーでの評価."""
        proposals = [
            VendorProposal(
                vendor_name="OnlyVendor",
                proposal_summary="唯一の提案",
                initial_cost=20000000,
                annual_maintenance_cost=3000000,
                implementation_months=6,
                team_size=5,
                technology_stack=["React", "Python"],
                references=3,
                sla_uptime=99.5,
                support_hours="9x5",
            ),
        ]
        result = evaluate_vendors(sample_requirement, proposals)
        assert len(result.scores) == 1
        assert result.scores[0].recommendation == "最推奨"

    def test_vendor_strengths_weaknesses(
        self,
        sample_requirement: RFPRequirement,
        sample_proposals: list[VendorProposal],
    ) -> None:
        result = evaluate_vendors(sample_requirement, sample_proposals)
        for score in result.scores:
            assert len(score.strengths) > 0
