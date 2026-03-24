"""週次レポート生成サービスのテスト."""

from __future__ import annotations

from datetime import date

import pytest

from app.models import TaskProgress, TaskStatus, WeeklyReportInput
from app.services.report_generator import generate_weekly_report


@pytest.fixture()
def sample_report_input() -> WeeklyReportInput:
    """サンプルレポート入力."""
    return WeeklyReportInput(
        project_name="テストプロジェクト",
        report_date=date(2026, 3, 25),
        tasks=[
            TaskProgress(
                task_id="T1",
                task_name="設計",
                planned_start=date(2026, 1, 1),
                planned_end=date(2026, 2, 28),
                actual_start=date(2026, 1, 5),
                actual_end=date(2026, 3, 5),
                planned_cost=1000000,
                actual_cost=1100000,
                percent_complete=1.0,
                status=TaskStatus.COMPLETED,
            ),
            TaskProgress(
                task_id="T2",
                task_name="実装",
                planned_start=date(2026, 3, 1),
                planned_end=date(2026, 5, 31),
                actual_start=date(2026, 3, 10),
                planned_cost=3000000,
                actual_cost=800000,
                percent_complete=0.3,
                status=TaskStatus.IN_PROGRESS,
            ),
            TaskProgress(
                task_id="T3",
                task_name="テスト",
                planned_start=date(2026, 6, 1),
                planned_end=date(2026, 7, 31),
                planned_cost=1500000,
                actual_cost=0,
                percent_complete=0.0,
                status=TaskStatus.NOT_STARTED,
            ),
        ],
        highlights=["設計フェーズ完了", "新メンバー参加"],
        issues=["API仕様変更による手戻り"],
        next_week_plan=["実装スプリント3", "結合テスト準備"],
    )


class TestGenerateWeeklyReport:
    """generate_weekly_report のテスト."""

    def test_generates_japanese_summary(
        self, sample_report_input: WeeklyReportInput,
    ) -> None:
        report = generate_weekly_report(sample_report_input)
        assert "テストプロジェクト" in report.executive_summary_ja
        assert "週次レポート" in report.executive_summary_ja

    def test_generates_english_summary(
        self, sample_report_input: WeeklyReportInput,
    ) -> None:
        report = generate_weekly_report(sample_report_input)
        assert "Weekly Report" in report.executive_summary_en
        assert "Executive Summary" in report.executive_summary_en

    def test_generates_japanese_detail(
        self, sample_report_input: WeeklyReportInput,
    ) -> None:
        report = generate_weekly_report(sample_report_input)
        assert "詳細レポート" in report.detailed_report_ja
        assert "タスク詳細" in report.detailed_report_ja

    def test_generates_english_detail(
        self, sample_report_input: WeeklyReportInput,
    ) -> None:
        report = generate_weekly_report(sample_report_input)
        assert "Detailed Weekly Report" in report.detailed_report_en
        assert "Task Details" in report.detailed_report_en

    def test_includes_evm_metrics(
        self, sample_report_input: WeeklyReportInput,
    ) -> None:
        report = generate_weekly_report(sample_report_input)
        assert report.evm is not None
        assert report.evm.bac > 0

    def test_includes_risks(
        self, sample_report_input: WeeklyReportInput,
    ) -> None:
        report = generate_weekly_report(sample_report_input)
        assert isinstance(report.risks, list)

    def test_includes_action_items(
        self, sample_report_input: WeeklyReportInput,
    ) -> None:
        report = generate_weekly_report(sample_report_input)
        assert len(report.action_items) > 0

    def test_includes_highlights_in_summary(
        self, sample_report_input: WeeklyReportInput,
    ) -> None:
        report = generate_weekly_report(sample_report_input)
        assert "設計フェーズ完了" in report.executive_summary_ja

    def test_includes_issues_in_summary(
        self, sample_report_input: WeeklyReportInput,
    ) -> None:
        report = generate_weekly_report(sample_report_input)
        assert "API仕様変更" in report.executive_summary_ja

    def test_report_date_correct(
        self, sample_report_input: WeeklyReportInput,
    ) -> None:
        report = generate_weekly_report(sample_report_input)
        assert report.report_date == date(2026, 3, 25)

    def test_evm_in_detailed_report(
        self, sample_report_input: WeeklyReportInput,
    ) -> None:
        report = generate_weekly_report(sample_report_input)
        assert "SPI" in report.detailed_report_ja
        assert "CPI" in report.detailed_report_ja
        assert "EAC" in report.detailed_report_ja
