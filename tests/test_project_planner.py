"""プロジェクト計画AIサービスのテスト."""

from __future__ import annotations

from datetime import date

import pytest

from app.models import Methodology, ProjectInput, ProjectType
from app.services.project_planner import create_project_plan, get_project_summary


@pytest.fixture()
def sample_project_input() -> ProjectInput:
    """サンプルプロジェクト入力."""
    return ProjectInput(
        name="テストプロジェクト",
        description="テスト用プロジェクト",
        project_type=ProjectType.WEB_DEV,
        methodology=Methodology.SCRUM,
        start_date=date(2026, 4, 1),
        target_end_date=date(2026, 9, 30),
        team_size=8,
        budget_jpy=50000000,
    )


class TestCreateProjectPlan:
    """create_project_plan のテスト."""

    def test_creates_plan_with_correct_name(
        self, sample_project_input: ProjectInput,
    ) -> None:
        plan = create_project_plan(sample_project_input)
        assert plan.project_name == "テストプロジェクト"

    def test_creates_plan_with_correct_type(
        self, sample_project_input: ProjectInput,
    ) -> None:
        plan = create_project_plan(sample_project_input)
        assert plan.project_type == ProjectType.WEB_DEV

    def test_creates_plan_with_tasks(
        self, sample_project_input: ProjectInput,
    ) -> None:
        plan = create_project_plan(sample_project_input)
        assert len(plan.tasks) > 0

    def test_creates_plan_with_phases(
        self, sample_project_input: ProjectInput,
    ) -> None:
        plan = create_project_plan(sample_project_input)
        assert len(plan.phases) > 0

    def test_creates_plan_with_milestones(
        self, sample_project_input: ProjectInput,
    ) -> None:
        plan = create_project_plan(sample_project_input)
        assert len(plan.milestones) > 0

    def test_creates_plan_with_critical_path(
        self, sample_project_input: ProjectInput,
    ) -> None:
        plan = create_project_plan(sample_project_input)
        assert len(plan.critical_path) > 0

    def test_creates_plan_with_gantt_data(
        self, sample_project_input: ProjectInput,
    ) -> None:
        plan = create_project_plan(sample_project_input)
        assert len(plan.gantt_data) > 0

    def test_total_estimated_days_positive(
        self, sample_project_input: ProjectInput,
    ) -> None:
        plan = create_project_plan(sample_project_input)
        assert plan.total_estimated_days > 0

    def test_scrum_methodology_applied(
        self, sample_project_input: ProjectInput,
    ) -> None:
        plan = create_project_plan(sample_project_input)
        assert plan.methodology == Methodology.SCRUM
        # Scrumオーバーレイが適用されていることを確認
        has_scrum_desc = any("Scrum" in p.description for p in plan.phases)
        assert has_scrum_desc

    def test_different_project_types(self) -> None:
        """異なるプロジェクト種別で計画が生成されることを確認."""
        for ptype in ProjectType:
            project_input = ProjectInput(
                name=f"Test {ptype.value}",
                description="Test",
                project_type=ptype,
                methodology=Methodology.SCRUM,
                start_date=date(2026, 4, 1),
                target_end_date=date(2026, 12, 31),
                team_size=5,
            )
            plan = create_project_plan(project_input)
            assert len(plan.tasks) > 0
            assert len(plan.phases) > 0

    def test_team_size_scaling(self) -> None:
        """大きなチームではタスク期間が短縮されることを確認."""
        small_input = ProjectInput(
            name="Small Team",
            description="Test",
            project_type=ProjectType.WEB_DEV,
            methodology=Methodology.SCRUM,
            start_date=date(2026, 4, 1),
            target_end_date=date(2026, 12, 31),
            team_size=2,
        )
        large_input = small_input.model_copy(update={
            "name": "Large Team",
            "team_size": 30,
        })

        small_plan = create_project_plan(small_input)
        large_plan = create_project_plan(large_input)

        # 大きなチームの方が合計日数が短い（スケーリング効果）
        assert large_plan.total_estimated_days < small_plan.total_estimated_days


class TestGetProjectSummary:
    """get_project_summary のテスト."""

    def test_summary_contains_required_keys(
        self, sample_project_input: ProjectInput,
    ) -> None:
        plan = create_project_plan(sample_project_input)
        summary = get_project_summary(plan)
        expected_keys = {
            "project_name",
            "project_type",
            "methodology",
            "total_tasks",
            "milestones",
            "critical_path_length",
            "total_estimated_days",
            "phases",
        }
        assert expected_keys == set(summary.keys())

    def test_summary_values_correct(
        self, sample_project_input: ProjectInput,
    ) -> None:
        plan = create_project_plan(sample_project_input)
        summary = get_project_summary(plan)
        assert summary["project_name"] == "テストプロジェクト"
        assert summary["project_type"] == "web_development"
        assert summary["methodology"] == "scrum"
