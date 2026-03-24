"""リスク分析AIサービスのテスト."""

from __future__ import annotations

from datetime import date

import pytest

from app.models import TaskProgress, TaskStatus
from app.services.risk_analyzer import analyze_risks


@pytest.fixture()
def healthy_tasks() -> list[TaskProgress]:
    """健全なプロジェクトタスク."""
    return [
        TaskProgress(
            task_id="T1",
            task_name="要件定義",
            planned_start=date(2026, 1, 1),
            planned_end=date(2026, 1, 31),
            actual_start=date(2026, 1, 1),
            actual_end=date(2026, 1, 30),
            planned_cost=500000,
            actual_cost=480000,
            percent_complete=1.0,
            status=TaskStatus.COMPLETED,
        ),
        TaskProgress(
            task_id="T2",
            task_name="設計",
            planned_start=date(2026, 2, 1),
            planned_end=date(2026, 2, 28),
            actual_start=date(2026, 2, 1),
            planned_cost=800000,
            actual_cost=400000,
            percent_complete=0.5,
            status=TaskStatus.IN_PROGRESS,
        ),
    ]


@pytest.fixture()
def delayed_tasks() -> list[TaskProgress]:
    """遅延プロジェクトタスク."""
    return [
        TaskProgress(
            task_id="T1",
            task_name="要件定義",
            planned_start=date(2026, 1, 1),
            planned_end=date(2026, 1, 31),
            actual_start=date(2026, 1, 10),
            planned_cost=500000,
            actual_cost=700000,
            percent_complete=0.8,
            status=TaskStatus.DELAYED,
        ),
        TaskProgress(
            task_id="T2",
            task_name="設計",
            planned_start=date(2026, 2, 1),
            planned_end=date(2026, 2, 28),
            planned_cost=800000,
            actual_cost=100000,
            percent_complete=0.1,
            status=TaskStatus.DELAYED,
        ),
        TaskProgress(
            task_id="T3",
            task_name="実装",
            planned_start=date(2026, 3, 1),
            planned_end=date(2026, 4, 30),
            planned_cost=2000000,
            actual_cost=0,
            percent_complete=0.0,
            status=TaskStatus.NOT_STARTED,
        ),
    ]


class TestAnalyzeRisks:
    """analyze_risks のテスト."""

    def test_returns_evm_metrics(self, healthy_tasks: list[TaskProgress]) -> None:
        result = analyze_risks(healthy_tasks, date(2026, 2, 15))
        assert result.evm is not None
        assert result.evm.bac > 0

    def test_healthy_project_has_healthy_status(
        self, healthy_tasks: list[TaskProgress],
    ) -> None:
        result = analyze_risks(healthy_tasks, date(2026, 2, 15))
        # 健全なプロジェクトはWARNINGかHEALTHY
        assert result.health_status in ("HEALTHY", "WARNING")

    def test_delayed_project_has_risks(
        self, delayed_tasks: list[TaskProgress],
    ) -> None:
        result = analyze_risks(delayed_tasks, date(2026, 3, 15))
        assert len(result.risk_register) > 0

    def test_delayed_project_has_high_delay_probability(
        self, delayed_tasks: list[TaskProgress],
    ) -> None:
        result = analyze_risks(delayed_tasks, date(2026, 3, 15))
        assert result.delay_probability > 0

    def test_recommendations_not_empty(
        self, healthy_tasks: list[TaskProgress],
    ) -> None:
        result = analyze_risks(healthy_tasks, date(2026, 2, 15))
        assert len(result.recommendations) > 0

    def test_evm_spi_calculation(
        self, healthy_tasks: list[TaskProgress],
    ) -> None:
        result = analyze_risks(healthy_tasks, date(2026, 2, 15))
        # SPI = EV / PV, should be a reasonable number
        assert result.evm.spi >= 0

    def test_evm_cpi_calculation(
        self, healthy_tasks: list[TaskProgress],
    ) -> None:
        result = analyze_risks(healthy_tasks, date(2026, 2, 15))
        # CPI = EV / AC
        assert result.evm.cpi >= 0

    def test_evm_eac_calculation(
        self, healthy_tasks: list[TaskProgress],
    ) -> None:
        result = analyze_risks(healthy_tasks, date(2026, 2, 15))
        assert result.evm.eac >= 0

    def test_budget_overrun_probability_range(
        self, delayed_tasks: list[TaskProgress],
    ) -> None:
        result = analyze_risks(delayed_tasks, date(2026, 3, 15))
        assert 0 <= result.budget_overrun_probability <= 1.0

    def test_delay_probability_range(
        self, delayed_tasks: list[TaskProgress],
    ) -> None:
        result = analyze_risks(delayed_tasks, date(2026, 3, 15))
        assert 0 <= result.delay_probability <= 1.0

    def test_blocked_tasks_generate_risk(self) -> None:
        """ブロックされたタスクがリスクを生成することを確認."""
        tasks = [
            TaskProgress(
                task_id="T1",
                task_name="ブロックタスク",
                planned_start=date(2026, 1, 1),
                planned_end=date(2026, 2, 28),
                planned_cost=1000000,
                actual_cost=500000,
                percent_complete=0.3,
                status=TaskStatus.BLOCKED,
            ),
        ]
        result = analyze_risks(tasks, date(2026, 2, 15))
        blocked_risks = [
            r for r in result.risk_register
            if "ブロック" in r.description
        ]
        assert len(blocked_risks) > 0

    def test_empty_reference_date_uses_today(
        self, healthy_tasks: list[TaskProgress],
    ) -> None:
        """reference_date=Noneでも動作することを確認."""
        result = analyze_risks(healthy_tasks, None)
        assert result.evm is not None
