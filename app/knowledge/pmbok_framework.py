"""PMBOK 7th Edition フレームワーク.

PMBOK 7th Edition の12原則と8パフォーマンスドメインを定義。
プロジェクト計画・リスク分析・レポート生成で参照される。
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class PMBOKPrinciple:
    """PMBOK原則."""

    principle_id: str
    name_en: str
    name_ja: str
    description: str


@dataclass(frozen=True)
class PerformanceDomain:
    """パフォーマンスドメイン."""

    domain_id: str
    name_en: str
    name_ja: str
    description: str
    key_activities: tuple[str, ...]
    outcomes: tuple[str, ...]


# PMBOK 7th Edition 12 Principles
PMBOK_PRINCIPLES: tuple[PMBOKPrinciple, ...] = (
    PMBOKPrinciple(
        "P01", "Stewardship", "スチュワードシップ",
        "責任ある行動、誠実さ、信頼、コンプライアンスの維持",
    ),
    PMBOKPrinciple(
        "P02", "Team", "チーム",
        "協力的なチーム環境の構築と個人の成長支援",
    ),
    PMBOKPrinciple(
        "P03", "Stakeholders", "ステークホルダー",
        "ステークホルダーとの効果的なエンゲージメント",
    ),
    PMBOKPrinciple(
        "P04", "Value", "価値",
        "価値の提供に焦点を当てる",
    ),
    PMBOKPrinciple(
        "P05", "Systems Thinking", "システム思考",
        "全体的な視点でシステムの相互作用を認識",
    ),
    PMBOKPrinciple(
        "P06", "Leadership", "リーダーシップ",
        "リーダーシップ行動の促進と適応",
    ),
    PMBOKPrinciple(
        "P07", "Tailoring", "テーラリング",
        "コンテキストに基づくアプローチの調整",
    ),
    PMBOKPrinciple(
        "P08", "Quality", "品質",
        "プロセスと成果物への品質組み込み",
    ),
    PMBOKPrinciple(
        "P09", "Complexity", "複雑性",
        "複雑性への対応と適応",
    ),
    PMBOKPrinciple(
        "P10", "Risk", "リスク",
        "リスク対応の最適化",
    ),
    PMBOKPrinciple(
        "P11", "Adaptability and Resilience", "適応性とレジリエンス",
        "変化への適応と回復力の構築",
    ),
    PMBOKPrinciple(
        "P12", "Change", "変革",
        "望ましい将来の状態を達成するための変革推進",
    ),
)

# PMBOK 7th Edition 8 Performance Domains
PERFORMANCE_DOMAINS: tuple[PerformanceDomain, ...] = (
    PerformanceDomain(
        "PD01", "Stakeholder", "ステークホルダー",
        "ステークホルダーとの関係構築・維持",
        key_activities=(
            "ステークホルダー特定",
            "期待値分析",
            "エンゲージメント戦略策定",
            "コミュニケーション管理",
        ),
        outcomes=(
            "生産的なワーキングリレーションシップ",
            "ステークホルダーの合意",
            "プロジェクト目標への賛同",
        ),
    ),
    PerformanceDomain(
        "PD02", "Team", "チーム",
        "チームパフォーマンスの最大化",
        key_activities=(
            "チーム編成",
            "スキル開発",
            "コンフリクト管理",
            "パフォーマンス評価",
        ),
        outcomes=(
            "共有されたオーナーシップ",
            "高パフォーマンスチーム",
            "適切なリーダーシップ",
        ),
    ),
    PerformanceDomain(
        "PD03", "Development Approach and Life Cycle", "開発アプローチとライフサイクル",
        "プロジェクトの開発アプローチとライフサイクルの定義",
        key_activities=(
            "開発アプローチ選定",
            "ライフサイクル定義",
            "フェーズ・ゲート設計",
            "デリバリー頻度決定",
        ),
        outcomes=(
            "適切な開発アプローチ",
            "成果物に適したライフサイクル",
            "段階的な価値提供",
        ),
    ),
    PerformanceDomain(
        "PD04", "Planning", "計画",
        "プロジェクト計画の策定と維持",
        key_activities=(
            "スコープ定義",
            "スケジュール策定",
            "コスト見積もり",
            "リソース計画",
            "WBS作成",
        ),
        outcomes=(
            "組織化された計画的な遂行",
            "全体的なアプローチの調整",
            "時間軸に沿った進化",
        ),
    ),
    PerformanceDomain(
        "PD05", "Project Work", "プロジェクト作業",
        "プロジェクト作業の実行・管理",
        key_activities=(
            "作業実行",
            "変更管理",
            "調達管理",
            "知識管理",
        ),
        outcomes=(
            "効率的なパフォーマンス",
            "適切なリソース管理",
            "継続的な学習",
        ),
    ),
    PerformanceDomain(
        "PD06", "Delivery", "デリバリー",
        "価値の提供",
        key_activities=(
            "要件管理",
            "スコープ管理",
            "品質管理",
            "受入確認",
        ),
        outcomes=(
            "ビジネス価値の実現",
            "成果物の受入",
            "品質基準の達成",
        ),
    ),
    PerformanceDomain(
        "PD07", "Measurement", "測定",
        "パフォーマンス測定と分析",
        key_activities=(
            "KPI設定",
            "EVM計算",
            "進捗追跡",
            "予測分析",
        ),
        outcomes=(
            "信頼性の高い理解",
            "データ駆動の意思決定",
            "タイムリーなアクション",
        ),
    ),
    PerformanceDomain(
        "PD08", "Uncertainty", "不確実性",
        "不確実性とリスクへの対応",
        key_activities=(
            "リスク特定",
            "リスク分析",
            "リスク対応計画",
            "リスクモニタリング",
        ),
        outcomes=(
            "脅威の影響最小化",
            "機会の最大活用",
            "不確実性の範囲内での意思決定",
        ),
    ),
)


@dataclass
class PMBOKFramework:
    """PMBOKフレームワーク統合クラス."""

    principles: tuple[PMBOKPrinciple, ...] = field(
        default=PMBOK_PRINCIPLES,
    )
    domains: tuple[PerformanceDomain, ...] = field(
        default=PERFORMANCE_DOMAINS,
    )

    def get_principle(self, principle_id: str) -> PMBOKPrinciple | None:
        """原則をIDで取得."""
        for p in self.principles:
            if p.principle_id == principle_id:
                return p
        return None

    def get_domain(self, domain_id: str) -> PerformanceDomain | None:
        """ドメインをIDで取得."""
        for d in self.domains:
            if d.domain_id == domain_id:
                return d
        return None

    def get_planning_activities(self) -> tuple[str, ...]:
        """計画ドメインのアクティビティを取得."""
        domain = self.get_domain("PD04")
        if domain:
            return domain.key_activities
        return ()

    def get_risk_activities(self) -> tuple[str, ...]:
        """不確実性ドメインのアクティビティを取得."""
        domain = self.get_domain("PD08")
        if domain:
            return domain.key_activities
        return ()

    def get_measurement_activities(self) -> tuple[str, ...]:
        """測定ドメインのアクティビティを取得."""
        domain = self.get_domain("PD07")
        if domain:
            return domain.key_activities
        return ()
