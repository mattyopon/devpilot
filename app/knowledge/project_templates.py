"""プロジェクトテンプレート.

5種類以上のWBSテンプレートを提供する。
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TemplateTask:
    """テンプレートタスク."""

    task_id: str
    name: str
    description: str
    parent_id: str | None = None
    dependencies: tuple[str, ...] = ()
    optimistic_days: float = 0
    most_likely_days: float = 0
    pessimistic_days: float = 0
    assigned_role: str | None = None
    is_milestone: bool = False


@dataclass(frozen=True)
class ProjectTemplate:
    """プロジェクトテンプレート."""

    template_id: str
    name: str
    description: str
    project_type: str
    phases: tuple[str, ...]
    tasks: tuple[TemplateTask, ...]
    recommended_team_roles: tuple[str, ...]
    typical_duration_months: tuple[int, int]  # (min, max)


def _web_dev_template() -> ProjectTemplate:
    """Web開発テンプレート."""
    return ProjectTemplate(
        template_id="TPL-WEB",
        name="Web Application Development",
        description="Webアプリケーション開発プロジェクトの標準WBS",
        project_type="web_development",
        phases=("要件定義", "設計", "開発", "テスト", "デプロイ", "運用移行"),
        tasks=(
            TemplateTask("W001", "要件ヒアリング", "ステークホルダーからの要件収集",
                         optimistic_days=3, most_likely_days=5, pessimistic_days=10,
                         assigned_role="BA"),
            TemplateTask("W002", "要件定義書作成", "要件の文書化", parent_id=None,
                         dependencies=("W001",),
                         optimistic_days=3, most_likely_days=5, pessimistic_days=8,
                         assigned_role="BA"),
            TemplateTask("W003", "要件定義完了", "マイルストーン", dependencies=("W002",),
                         is_milestone=True),
            TemplateTask("W004", "UI/UXデザイン", "画面設計・ワイヤーフレーム",
                         dependencies=("W003",),
                         optimistic_days=5, most_likely_days=10, pessimistic_days=15,
                         assigned_role="Designer"),
            TemplateTask("W005", "システム設計", "アーキテクチャ・DB設計",
                         dependencies=("W003",),
                         optimistic_days=5, most_likely_days=8, pessimistic_days=12,
                         assigned_role="Architect"),
            TemplateTask("W006", "設計レビュー", "設計の承認", dependencies=("W004", "W005"),
                         optimistic_days=1, most_likely_days=2, pessimistic_days=3,
                         assigned_role="Tech Lead", is_milestone=True),
            TemplateTask("W007", "フロントエンド開発", "UI実装",
                         dependencies=("W006",),
                         optimistic_days=15, most_likely_days=25, pessimistic_days=40,
                         assigned_role="FE Developer"),
            TemplateTask("W008", "バックエンド開発", "API・ビジネスロジック実装",
                         dependencies=("W006",),
                         optimistic_days=15, most_likely_days=25, pessimistic_days=40,
                         assigned_role="BE Developer"),
            TemplateTask("W009", "結合テスト", "E2E・結合テスト",
                         dependencies=("W007", "W008"),
                         optimistic_days=5, most_likely_days=10, pessimistic_days=15,
                         assigned_role="QA"),
            TemplateTask("W010", "UAT", "ユーザー受入テスト", dependencies=("W009",),
                         optimistic_days=3, most_likely_days=5, pessimistic_days=10,
                         assigned_role="BA"),
            TemplateTask("W011", "デプロイ", "本番環境デプロイ", dependencies=("W010",),
                         optimistic_days=1, most_likely_days=2, pessimistic_days=5,
                         assigned_role="DevOps"),
            TemplateTask("W012", "運用移行", "運用チームへの引き渡し",
                         dependencies=("W011",),
                         optimistic_days=2, most_likely_days=3, pessimistic_days=5,
                         assigned_role="PM"),
        ),
        recommended_team_roles=(
            "PM", "BA", "Architect", "Designer",
            "FE Developer", "BE Developer", "QA", "DevOps",
        ),
        typical_duration_months=(3, 9),
    )


def _infra_template() -> ProjectTemplate:
    """インフラ構築テンプレート."""
    return ProjectTemplate(
        template_id="TPL-INFRA",
        name="Infrastructure Setup",
        description="インフラ構築・移行プロジェクトの標準WBS",
        project_type="infrastructure",
        phases=("現状分析", "設計", "構築", "移行", "検証", "運用開始"),
        tasks=(
            TemplateTask("I001", "現状インフラ調査", "既存環境の棚卸し",
                         optimistic_days=3, most_likely_days=5, pessimistic_days=8,
                         assigned_role="Infra Engineer"),
            TemplateTask("I002", "要件整理", "非機能要件の定義",
                         dependencies=("I001",),
                         optimistic_days=2, most_likely_days=4, pessimistic_days=6,
                         assigned_role="Architect"),
            TemplateTask("I003", "アーキテクチャ設計", "インフラ設計",
                         dependencies=("I002",),
                         optimistic_days=5, most_likely_days=8, pessimistic_days=12,
                         assigned_role="Architect"),
            TemplateTask("I004", "環境構築", "インフラ構築",
                         dependencies=("I003",),
                         optimistic_days=10, most_likely_days=15, pessimistic_days=25,
                         assigned_role="Infra Engineer"),
            TemplateTask("I005", "移行計画策定", "データ移行・切替計画",
                         dependencies=("I003",),
                         optimistic_days=3, most_likely_days=5, pessimistic_days=8,
                         assigned_role="PM"),
            TemplateTask("I006", "移行実行", "データ移行・環境切替",
                         dependencies=("I004", "I005"),
                         optimistic_days=3, most_likely_days=7, pessimistic_days=14,
                         assigned_role="Infra Engineer"),
            TemplateTask("I007", "検証テスト", "性能・可用性テスト",
                         dependencies=("I006",),
                         optimistic_days=3, most_likely_days=5, pessimistic_days=10,
                         assigned_role="QA"),
            TemplateTask("I008", "運用開始", "本番稼働",
                         dependencies=("I007",),
                         optimistic_days=1, most_likely_days=2, pessimistic_days=3,
                         assigned_role="Infra Engineer", is_milestone=True),
        ),
        recommended_team_roles=(
            "PM", "Architect", "Infra Engineer", "Network Engineer",
            "Security Engineer", "QA",
        ),
        typical_duration_months=(2, 6),
    )


def _erp_template() -> ProjectTemplate:
    """ERP導入テンプレート."""
    return ProjectTemplate(
        template_id="TPL-ERP",
        name="ERP Implementation",
        description="ERP導入プロジェクトの標準WBS",
        project_type="erp_implementation",
        phases=("計画", "要件定義", "Fit/Gap分析", "設計・設定", "テスト", "移行", "Go-Live"),
        tasks=(
            TemplateTask("E001", "プロジェクト計画", "スコープ・体制・スケジュール策定",
                         optimistic_days=5, most_likely_days=10, pessimistic_days=15,
                         assigned_role="PM"),
            TemplateTask("E002", "業務プロセス分析", "As-Is業務フロー分析",
                         dependencies=("E001",),
                         optimistic_days=10, most_likely_days=20, pessimistic_days=30,
                         assigned_role="Business Consultant"),
            TemplateTask("E003", "Fit/Gap分析", "標準機能とのギャップ分析",
                         dependencies=("E002",),
                         optimistic_days=10, most_likely_days=15, pessimistic_days=25,
                         assigned_role="ERP Consultant"),
            TemplateTask("E004", "To-Be設計", "目標業務プロセス設計",
                         dependencies=("E003",),
                         optimistic_days=10, most_likely_days=15, pessimistic_days=20,
                         assigned_role="ERP Consultant"),
            TemplateTask("E005", "ERP設定・カスタマイズ", "システム設定とアドオン開発",
                         dependencies=("E004",),
                         optimistic_days=20, most_likely_days=40, pessimistic_days=60,
                         assigned_role="ERP Developer"),
            TemplateTask("E006", "単体・結合テスト", "機能テスト",
                         dependencies=("E005",),
                         optimistic_days=10, most_likely_days=15, pessimistic_days=25,
                         assigned_role="QA"),
            TemplateTask("E007", "UAT", "ユーザー受入テスト",
                         dependencies=("E006",),
                         optimistic_days=10, most_likely_days=15, pessimistic_days=20,
                         assigned_role="Business User"),
            TemplateTask("E008", "データ移行", "マスタ・トランザクション移行",
                         dependencies=("E006",),
                         optimistic_days=5, most_likely_days=10, pessimistic_days=20,
                         assigned_role="Data Engineer"),
            TemplateTask("E009", "トレーニング", "ユーザー教育",
                         dependencies=("E007",),
                         optimistic_days=5, most_likely_days=10, pessimistic_days=15,
                         assigned_role="Trainer"),
            TemplateTask("E010", "Go-Live", "本番稼働",
                         dependencies=("E007", "E008", "E009"),
                         optimistic_days=2, most_likely_days=3, pessimistic_days=5,
                         assigned_role="PM", is_milestone=True),
        ),
        recommended_team_roles=(
            "PM", "Business Consultant", "ERP Consultant",
            "ERP Developer", "Data Engineer", "QA", "Trainer", "Change Manager",
        ),
        typical_duration_months=(6, 18),
    )


def _mobile_template() -> ProjectTemplate:
    """モバイルアプリテンプレート."""
    return ProjectTemplate(
        template_id="TPL-MOBILE",
        name="Mobile App Development",
        description="モバイルアプリ開発プロジェクトの標準WBS",
        project_type="mobile_app",
        phases=("企画", "設計", "開発", "テスト", "リリース"),
        tasks=(
            TemplateTask("M001", "市場調査・企画", "ターゲット・機能の策定",
                         optimistic_days=3, most_likely_days=5, pessimistic_days=8,
                         assigned_role="Product Manager"),
            TemplateTask("M002", "UI/UXデザイン", "プロトタイプ作成",
                         dependencies=("M001",),
                         optimistic_days=5, most_likely_days=10, pessimistic_days=15,
                         assigned_role="UI/UX Designer"),
            TemplateTask("M003", "API設計", "バックエンドAPI設計",
                         dependencies=("M001",),
                         optimistic_days=3, most_likely_days=5, pessimistic_days=8,
                         assigned_role="Architect"),
            TemplateTask("M004", "iOS開発", "iOS版実装",
                         dependencies=("M002", "M003"),
                         optimistic_days=15, most_likely_days=25, pessimistic_days=40,
                         assigned_role="iOS Developer"),
            TemplateTask("M005", "Android開発", "Android版実装",
                         dependencies=("M002", "M003"),
                         optimistic_days=15, most_likely_days=25, pessimistic_days=40,
                         assigned_role="Android Developer"),
            TemplateTask("M006", "バックエンド開発", "API・サーバー実装",
                         dependencies=("M003",),
                         optimistic_days=10, most_likely_days=20, pessimistic_days=30,
                         assigned_role="BE Developer"),
            TemplateTask("M007", "QAテスト", "端末テスト・パフォーマンステスト",
                         dependencies=("M004", "M005", "M006"),
                         optimistic_days=5, most_likely_days=10, pessimistic_days=15,
                         assigned_role="QA"),
            TemplateTask("M008", "ストア申請・リリース", "App Store / Google Play申請",
                         dependencies=("M007",),
                         optimistic_days=3, most_likely_days=5, pessimistic_days=10,
                         assigned_role="DevOps", is_milestone=True),
        ),
        recommended_team_roles=(
            "Product Manager", "UI/UX Designer", "Architect",
            "iOS Developer", "Android Developer", "BE Developer", "QA", "DevOps",
        ),
        typical_duration_months=(3, 9),
    )


def _ai_ml_template() -> ProjectTemplate:
    """AI/MLテンプレート."""
    return ProjectTemplate(
        template_id="TPL-AIML",
        name="AI/ML Project",
        description="AI/ML開発プロジェクトの標準WBS",
        project_type="ai_ml",
        phases=("問題定義", "データ収集", "探索・前処理", "モデル開発", "評価", "デプロイ", "モニタリング"),
        tasks=(
            TemplateTask("A001", "問題定義・KPI設定", "ビジネス課題のML問題への変換",
                         optimistic_days=3, most_likely_days=5, pessimistic_days=8,
                         assigned_role="Data Scientist"),
            TemplateTask("A002", "データ収集・連携", "データソース特定・パイプライン構築",
                         dependencies=("A001",),
                         optimistic_days=5, most_likely_days=10, pessimistic_days=20,
                         assigned_role="Data Engineer"),
            TemplateTask("A003", "EDA・データ前処理", "探索的データ分析・クレンジング",
                         dependencies=("A002",),
                         optimistic_days=5, most_likely_days=10, pessimistic_days=15,
                         assigned_role="Data Scientist"),
            TemplateTask("A004", "特徴量エンジニアリング", "特徴量の設計・作成",
                         dependencies=("A003",),
                         optimistic_days=5, most_likely_days=8, pessimistic_days=15,
                         assigned_role="ML Engineer"),
            TemplateTask("A005", "モデル開発・学習", "モデル選定・学習・チューニング",
                         dependencies=("A004",),
                         optimistic_days=10, most_likely_days=20, pessimistic_days=35,
                         assigned_role="ML Engineer"),
            TemplateTask("A006", "モデル評価", "精度・公平性・ロバスト性の評価",
                         dependencies=("A005",),
                         optimistic_days=3, most_likely_days=5, pessimistic_days=8,
                         assigned_role="Data Scientist"),
            TemplateTask("A007", "MLOpsパイプライン構築", "CI/CD・モデルレジストリ",
                         dependencies=("A006",),
                         optimistic_days=5, most_likely_days=10, pessimistic_days=15,
                         assigned_role="MLOps Engineer"),
            TemplateTask("A008", "本番デプロイ", "モデルサービング",
                         dependencies=("A007",),
                         optimistic_days=2, most_likely_days=5, pessimistic_days=8,
                         assigned_role="MLOps Engineer"),
            TemplateTask("A009", "モニタリング設定", "ドリフト検知・アラート",
                         dependencies=("A008",),
                         optimistic_days=3, most_likely_days=5, pessimistic_days=8,
                         assigned_role="MLOps Engineer", is_milestone=True),
        ),
        recommended_team_roles=(
            "PM", "Data Scientist", "ML Engineer",
            "Data Engineer", "MLOps Engineer", "Domain Expert",
        ),
        typical_duration_months=(3, 12),
    )


def _data_platform_template() -> ProjectTemplate:
    """データ基盤構築テンプレート."""
    return ProjectTemplate(
        template_id="TPL-DATA",
        name="Data Platform Construction",
        description="データ基盤構築プロジェクトの標準WBS",
        project_type="infrastructure",
        phases=("要件定義", "アーキテクチャ設計", "構築", "データ統合", "テスト", "運用開始"),
        tasks=(
            TemplateTask("D001", "データ要件収集", "利用者ニーズ・データソース特定",
                         optimistic_days=5, most_likely_days=8, pessimistic_days=12,
                         assigned_role="Data Architect"),
            TemplateTask("D002", "アーキテクチャ設計", "データレイク/DWH設計",
                         dependencies=("D001",),
                         optimistic_days=5, most_likely_days=10, pessimistic_days=15,
                         assigned_role="Data Architect"),
            TemplateTask("D003", "基盤構築", "クラウド環境・ツール導入",
                         dependencies=("D002",),
                         optimistic_days=10, most_likely_days=15, pessimistic_days=25,
                         assigned_role="Data Engineer"),
            TemplateTask("D004", "ETLパイプライン開発", "データ取込・変換処理",
                         dependencies=("D003",),
                         optimistic_days=10, most_likely_days=20, pessimistic_days=30,
                         assigned_role="Data Engineer"),
            TemplateTask("D005", "データ品質チェック", "品質ルール・モニタリング",
                         dependencies=("D004",),
                         optimistic_days=3, most_likely_days=5, pessimistic_days=8,
                         assigned_role="Data Engineer"),
            TemplateTask("D006", "BIダッシュボード構築", "分析用ダッシュボード作成",
                         dependencies=("D004",),
                         optimistic_days=5, most_likely_days=10, pessimistic_days=15,
                         assigned_role="BI Developer"),
            TemplateTask("D007", "運用開始", "本番稼働・運用引き渡し",
                         dependencies=("D005", "D006"),
                         optimistic_days=2, most_likely_days=3, pessimistic_days=5,
                         assigned_role="PM", is_milestone=True),
        ),
        recommended_team_roles=(
            "PM", "Data Architect", "Data Engineer",
            "BI Developer", "Security Engineer",
        ),
        typical_duration_months=(3, 9),
    )


# テンプレートレジストリ
ALL_TEMPLATES: dict[str, ProjectTemplate] = {
    "web_development": _web_dev_template(),
    "infrastructure": _infra_template(),
    "erp_implementation": _erp_template(),
    "mobile_app": _mobile_template(),
    "ai_ml": _ai_ml_template(),
    "data_platform": _data_platform_template(),
}


def get_template(project_type: str) -> ProjectTemplate | None:
    """プロジェクト種別からテンプレートを取得."""
    return ALL_TEMPLATES.get(project_type)


def get_all_template_names() -> list[str]:
    """全テンプレート名を取得."""
    return [t.name for t in ALL_TEMPLATES.values()]
