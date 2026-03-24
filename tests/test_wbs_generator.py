"""WBS自動生成サービスのテスト."""

from __future__ import annotations

from datetime import date


from app.models import ProjectType
from app.services.wbs_generator import (
    calculate_critical_path,
    calculate_pert_estimate,
    generate_wbs,
)


class TestCalculatePertEstimate:
    """PERT見積もりのテスト."""

    def test_symmetric_estimate(self) -> None:
        result = calculate_pert_estimate(4, 6, 8)
        assert result == 6.0

    def test_optimistic_skew(self) -> None:
        result = calculate_pert_estimate(1, 2, 3)
        assert result == 2.0

    def test_pessimistic_skew(self) -> None:
        result = calculate_pert_estimate(2, 5, 20)
        # (2 + 20 + 20) / 6 = 7.0
        expected = (2 + 4 * 5 + 20) / 6
        assert abs(result - expected) < 0.01

    def test_zero_values(self) -> None:
        result = calculate_pert_estimate(0, 0, 0)
        assert result == 0.0

    def test_large_variance(self) -> None:
        result = calculate_pert_estimate(1, 10, 100)
        expected = (1 + 40 + 100) / 6
        assert abs(result - expected) < 0.01


class TestGenerateWbs:
    """WBS生成のテスト."""

    def test_web_development_wbs(self) -> None:
        result = generate_wbs(
            ProjectType.WEB_DEV,
            "テストWeb",
            date(2026, 4, 1),
        )
        assert len(result["tasks"]) > 0
        assert result["template_name"] == "Web Application Development"

    def test_infrastructure_wbs(self) -> None:
        result = generate_wbs(
            ProjectType.INFRASTRUCTURE,
            "テストInfra",
            date(2026, 4, 1),
        )
        assert len(result["tasks"]) > 0
        assert result["template_name"] == "Infrastructure Setup"

    def test_erp_wbs(self) -> None:
        result = generate_wbs(
            ProjectType.ERP,
            "テストERP",
            date(2026, 4, 1),
        )
        assert len(result["tasks"]) > 0
        assert result["template_name"] == "ERP Implementation"

    def test_mobile_wbs(self) -> None:
        result = generate_wbs(
            ProjectType.MOBILE,
            "テストMobile",
            date(2026, 4, 1),
        )
        assert len(result["tasks"]) > 0

    def test_ai_ml_wbs(self) -> None:
        result = generate_wbs(
            ProjectType.AI_ML,
            "テストAI",
            date(2026, 4, 1),
        )
        assert len(result["tasks"]) > 0

    def test_wbs_has_critical_path(self) -> None:
        result = generate_wbs(
            ProjectType.WEB_DEV,
            "テスト",
            date(2026, 4, 1),
        )
        assert len(result["critical_path"]) > 0

    def test_wbs_has_milestones(self) -> None:
        result = generate_wbs(
            ProjectType.WEB_DEV,
            "テスト",
            date(2026, 4, 1),
        )
        assert len(result["milestones"]) > 0

    def test_wbs_has_gantt_data(self) -> None:
        result = generate_wbs(
            ProjectType.WEB_DEV,
            "テスト",
            date(2026, 4, 1),
        )
        assert len(result["gantt_data"]) > 0

    def test_wbs_has_phases(self) -> None:
        result = generate_wbs(
            ProjectType.WEB_DEV,
            "テスト",
            date(2026, 4, 1),
        )
        assert len(result["phases"]) > 0

    def test_total_estimated_days_positive(self) -> None:
        result = generate_wbs(
            ProjectType.WEB_DEV,
            "テスト",
            date(2026, 4, 1),
        )
        assert result["total_estimated_days"] > 0

    def test_tasks_have_dates(self) -> None:
        result = generate_wbs(
            ProjectType.WEB_DEV,
            "テスト",
            date(2026, 4, 1),
        )
        for task in result["tasks"]:
            assert task.start_date is not None
            assert task.end_date is not None

    def test_critical_path_tasks_flagged(self) -> None:
        result = generate_wbs(
            ProjectType.WEB_DEV,
            "テスト",
            date(2026, 4, 1),
        )
        critical_ids = set(result["critical_path"])
        for task in result["tasks"]:
            if task.task_id in critical_ids:
                assert task.is_critical_path


class TestCalculateCriticalPath:
    """クリティカルパス計算のテスト."""

    def test_empty_tasks(self) -> None:
        result = calculate_critical_path([])
        assert result == []

    def test_single_task(self) -> None:
        from app.models import WBSTask
        tasks = [
            WBSTask(
                task_id="T1",
                name="Task1",
                description="Test",
                dependencies=[],
                optimistic_days=1,
                most_likely_days=2,
                pessimistic_days=3,
                expected_days=2,
            ),
        ]
        result = calculate_critical_path(tasks)
        assert result == ["T1"]

    def test_linear_chain(self) -> None:
        from app.models import WBSTask
        tasks = [
            WBSTask(
                task_id="T1", name="A", description="",
                dependencies=[],
                optimistic_days=1, most_likely_days=2, pessimistic_days=3,
                expected_days=5,
            ),
            WBSTask(
                task_id="T2", name="B", description="",
                dependencies=["T1"],
                optimistic_days=1, most_likely_days=2, pessimistic_days=3,
                expected_days=3,
            ),
            WBSTask(
                task_id="T3", name="C", description="",
                dependencies=["T2"],
                optimistic_days=1, most_likely_days=2, pessimistic_days=3,
                expected_days=4,
            ),
        ]
        result = calculate_critical_path(tasks)
        assert set(result) == {"T1", "T2", "T3"}
