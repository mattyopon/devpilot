"""DevPilot Streamlit UI.

プロジェクト管理ダッシュボード。
"""

from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from app.models import (
    Methodology,
    ProjectInput,
    ProjectType,
    RFPRequirement,
    TaskProgress,
    TaskStatus,
    VendorProposal,
    WeeklyReportInput,
)
from app.services.project_planner import create_project_plan, get_project_summary
from app.services.report_generator import generate_weekly_report
from app.services.risk_analyzer import analyze_risks
from app.services.vendor_evaluator import evaluate_vendors

st.set_page_config(
    page_title="DevPilot - PM/PMO AI",
    page_icon="📊",
    layout="wide",
)

st.title("DevPilot - PM/PMO代替AI")
st.markdown("プロジェクト管理を自動化するAIアシスタント")

tab1, tab2, tab3, tab4 = st.tabs([
    "プロジェクト計画", "リスク分析", "週次レポート", "ベンダー評価",
])

with tab1:
    st.header("プロジェクト計画AI")
    col1, col2 = st.columns(2)

    with col1:
        proj_name = st.text_input("プロジェクト名", "新規Webシステム開発")
        proj_desc = st.text_area("概要", "社内業務管理システムのリプレイス")
        proj_type = st.selectbox(
            "種別",
            options=[t.value for t in ProjectType],
            format_func=lambda x: {
                "web_development": "Web開発",
                "infrastructure": "インフラ",
                "erp_implementation": "ERP導入",
                "mobile_app": "モバイル",
                "ai_ml": "AI/ML",
            }.get(x, x),
        )
        methodology = st.selectbox(
            "方法論",
            options=[m.value for m in Methodology],
        )

    with col2:
        start = st.date_input("開始日", date.today())
        end = st.date_input("目標終了日", date.today() + timedelta(days=180))
        team_size = st.number_input("チーム人数", min_value=1, max_value=500, value=8)
        budget = st.number_input("予算 (万円)", min_value=0, value=5000)

    if st.button("計画を生成", key="plan"):
        project_input = ProjectInput(
            name=proj_name,
            description=proj_desc,
            project_type=ProjectType(proj_type),
            methodology=Methodology(methodology),
            start_date=start,
            target_end_date=end,
            team_size=team_size,
            budget_jpy=budget * 10000,
        )
        plan = create_project_plan(project_input)
        summary = get_project_summary(plan)

        st.success("計画を生成しました")
        st.json(summary)

        st.subheader("WBSタスク一覧")
        task_data = [
            {
                "ID": t.task_id,
                "タスク": t.name,
                "見積日数": t.expected_days,
                "開始日": str(t.start_date),
                "終了日": str(t.end_date),
                "クリティカル": "Yes" if t.is_critical_path else "",
            }
            for t in plan.tasks
        ]
        st.dataframe(task_data, use_container_width=True)

with tab2:
    st.header("リスク分析AI")
    st.info("サンプルデータでリスク分析を実行します")

    if st.button("サンプル分析を実行", key="risk"):
        sample_tasks = [
            TaskProgress(
                task_id="T1", task_name="要件定義",
                planned_start=date(2026, 1, 1), planned_end=date(2026, 1, 31),
                actual_start=date(2026, 1, 5),
                planned_cost=500000, actual_cost=600000,
                percent_complete=1.0, status=TaskStatus.COMPLETED,
            ),
            TaskProgress(
                task_id="T2", task_name="設計",
                planned_start=date(2026, 2, 1), planned_end=date(2026, 2, 28),
                actual_start=date(2026, 2, 5),
                planned_cost=800000, actual_cost=750000,
                percent_complete=0.8, status=TaskStatus.IN_PROGRESS,
            ),
            TaskProgress(
                task_id="T3", task_name="実装",
                planned_start=date(2026, 3, 1), planned_end=date(2026, 4, 30),
                planned_cost=2000000, actual_cost=0,
                percent_complete=0.0, status=TaskStatus.NOT_STARTED,
            ),
        ]
        result = analyze_risks(sample_tasks, date(2026, 3, 1))
        st.metric("プロジェクト健全性", result.health_status)
        col1, col2, col3 = st.columns(3)
        col1.metric("SPI", f"{result.evm.spi:.2f}")
        col2.metric("CPI", f"{result.evm.cpi:.2f}")
        col3.metric("遅延確率", f"{result.delay_probability:.0%}")

        st.subheader("リスクレジスタ")
        for risk in result.risk_register:
            st.warning(f"[{risk.level.value.upper()}] {risk.description}")

with tab3:
    st.header("週次レポート自動生成")
    if st.button("サンプルレポート生成", key="report"):
        sample_input = WeeklyReportInput(
            project_name="サンプルプロジェクト",
            report_date=date.today(),
            tasks=[
                TaskProgress(
                    task_id="T1", task_name="設計",
                    planned_start=date(2026, 1, 1), planned_end=date(2026, 2, 28),
                    actual_start=date(2026, 1, 5),
                    planned_cost=1000000, actual_cost=900000,
                    percent_complete=0.9, status=TaskStatus.IN_PROGRESS,
                ),
                TaskProgress(
                    task_id="T2", task_name="実装",
                    planned_start=date(2026, 2, 1), planned_end=date(2026, 4, 30),
                    planned_cost=3000000, actual_cost=1500000,
                    percent_complete=0.4, status=TaskStatus.IN_PROGRESS,
                ),
            ],
            highlights=["設計フェーズがほぼ完了", "新メンバー2名がオンボーディング完了"],
            issues=["外部APIの仕様変更により一部手戻りが発生"],
            next_week_plan=["実装フェーズのスプリント3開始", "結合テスト準備"],
        )
        report = generate_weekly_report(sample_input)

        st.subheader("日本語サマリー")
        st.markdown(report.executive_summary_ja)

        st.subheader("English Summary")
        st.markdown(report.executive_summary_en)

with tab4:
    st.header("ベンダー評価AI")
    if st.button("サンプル評価を実行", key="vendor"):
        req = RFPRequirement(
            project_name="基幹システムリプレイス",
            project_type=ProjectType.WEB_DEV,
            scope="既存の基幹システムをクラウドネイティブに刷新",
            requirements=["マイクロサービスアーキテクチャ", "99.9% SLA", "24x7サポート"],
            budget_range_jpy=(50000000, 100000000),
            timeline_months=12,
        )
        proposals = [
            VendorProposal(
                vendor_name="TechCorp",
                proposal_summary="クラウドネイティブ全面刷新",
                initial_cost=80000000,
                annual_maintenance_cost=12000000,
                implementation_months=10,
                team_size=12,
                technology_stack=["React", "Go", "PostgreSQL", "Kubernetes", "AWS"],
                references=5,
                sla_uptime=99.95,
                support_hours="24x7",
            ),
            VendorProposal(
                vendor_name="SysCo",
                proposal_summary="段階的マイグレーション",
                initial_cost=60000000,
                annual_maintenance_cost=15000000,
                implementation_months=14,
                team_size=8,
                technology_stack=["Vue.js", "Java", "Oracle"],
                references=3,
                sla_uptime=99.5,
                support_hours="9x5",
            ),
        ]
        result = evaluate_vendors(req, proposals)
        st.success(result.recommendation)

        st.subheader("スコア比較")
        for score in result.scores:
            st.write(f"**{score.vendor_name}** - 総合: {score.total_score}/10")
            cols = st.columns(5)
            cols[0].metric("コスト", f"{score.cost_score}")
            cols[1].metric("技術", f"{score.technical_score}")
            cols[2].metric("実績", f"{score.experience_score}")
            cols[3].metric("期間", f"{score.timeline_score}")
            cols[4].metric("サポート", f"{score.support_score}")
