"""アジャイルフレームワーク定義.

Scrum / Kanban / SAFe のフレームワーク知識ベース。
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ScrumEvent:
    """Scrumイベント."""

    name: str
    timebox: str
    purpose: str
    participants: tuple[str, ...]


@dataclass(frozen=True)
class ScrumRole:
    """Scrumロール."""

    name: str
    responsibilities: tuple[str, ...]


@dataclass(frozen=True)
class ScrumArtifact:
    """Scrumアーティファクト."""

    name: str
    description: str
    commitment: str


SCRUM_ROLES: tuple[ScrumRole, ...] = (
    ScrumRole(
        "Product Owner",
        (
            "プロダクトバックログの管理",
            "ステークホルダーとの連携",
            "ROI最大化",
            "受入基準の定義",
        ),
    ),
    ScrumRole(
        "Scrum Master",
        (
            "スクラムの促進",
            "障害の除去",
            "チームのコーチング",
            "組織変革のリード",
        ),
    ),
    ScrumRole(
        "Developers",
        (
            "インクリメントの作成",
            "スプリントバックログの管理",
            "品質基準の遵守",
            "日次の適応",
        ),
    ),
)

SCRUM_EVENTS: tuple[ScrumEvent, ...] = (
    ScrumEvent(
        "Sprint Planning",
        "スプリント期間の8時間以内",
        "スプリントゴールの設定とバックログの選定",
        ("Product Owner", "Scrum Master", "Developers"),
    ),
    ScrumEvent(
        "Daily Scrum",
        "15分",
        "スプリントゴールに向けた進捗の確認と計画の適応",
        ("Developers",),
    ),
    ScrumEvent(
        "Sprint Review",
        "スプリント期間の4時間以内",
        "インクリメントの検査とバックログの適応",
        ("Product Owner", "Scrum Master", "Developers", "Stakeholders"),
    ),
    ScrumEvent(
        "Sprint Retrospective",
        "スプリント期間の3時間以内",
        "プロセスの検査と改善計画の策定",
        ("Product Owner", "Scrum Master", "Developers"),
    ),
)

SCRUM_ARTIFACTS: tuple[ScrumArtifact, ...] = (
    ScrumArtifact(
        "Product Backlog",
        "プロダクトに必要な改善の順序付きリスト",
        "Product Goal",
    ),
    ScrumArtifact(
        "Sprint Backlog",
        "スプリントゴール + 選択されたバックログアイテム + 計画",
        "Sprint Goal",
    ),
    ScrumArtifact(
        "Increment",
        "プロダクトゴールに向けた具体的な成果物",
        "Definition of Done",
    ),
)


@dataclass(frozen=True)
class KanbanPractice:
    """Kanbanプラクティス."""

    name: str
    description: str


KANBAN_PRACTICES: tuple[KanbanPractice, ...] = (
    KanbanPractice(
        "Visualize the Workflow",
        "作業フローをカンバンボードで可視化する",
    ),
    KanbanPractice(
        "Limit Work in Progress",
        "同時進行作業数を制限してフローを最適化する",
    ),
    KanbanPractice(
        "Manage Flow",
        "作業アイテムのフローを管理し、ボトルネックを解消する",
    ),
    KanbanPractice(
        "Make Policies Explicit",
        "プロセスルールを明示化する",
    ),
    KanbanPractice(
        "Implement Feedback Loops",
        "定期的なフィードバックループを実装する",
    ),
    KanbanPractice(
        "Improve Collaboratively, Evolve Experimentally",
        "協調的に改善し、実験的に進化する",
    ),
)


@dataclass(frozen=True)
class SAFeLevel:
    """SAFeレベル."""

    name: str
    description: str
    key_roles: tuple[str, ...]
    key_events: tuple[str, ...]


SAFE_LEVELS: tuple[SAFeLevel, ...] = (
    SAFeLevel(
        "Team",
        "アジャイルチームレベル（Scrum/Kanbanベース）",
        ("Scrum Master", "Product Owner", "Team Members"),
        ("Sprint Planning", "Daily Standup", "Sprint Review", "Retrospective"),
    ),
    SAFeLevel(
        "Program (ART)",
        "Agile Release Trainレベル",
        ("Release Train Engineer", "Product Manager", "System Architect"),
        ("PI Planning", "System Demo", "Inspect & Adapt"),
    ),
    SAFeLevel(
        "Large Solution",
        "大規模ソリューションレベル",
        ("Solution Train Engineer", "Solution Manager", "Solution Architect"),
        ("Pre-PI Planning", "Post-PI Planning", "Solution Demo"),
    ),
    SAFeLevel(
        "Portfolio",
        "ポートフォリオレベル",
        ("Lean Portfolio Management", "Enterprise Architect", "Epic Owners"),
        ("Portfolio Sync", "Strategic Themes Review", "Participatory Budgeting"),
    ),
)


@dataclass
class ScrumFramework:
    """Scrumフレームワーク."""

    roles: tuple[ScrumRole, ...] = field(default=SCRUM_ROLES)
    events: tuple[ScrumEvent, ...] = field(default=SCRUM_EVENTS)
    artifacts: tuple[ScrumArtifact, ...] = field(default=SCRUM_ARTIFACTS)
    sprint_duration_weeks: int = 2

    def get_ceremony_schedule(self) -> list[dict[str, str]]:
        """セレモニースケジュールを取得."""
        return [
            {"event": e.name, "timebox": e.timebox, "purpose": e.purpose}
            for e in self.events
        ]


@dataclass
class KanbanFramework:
    """Kanbanフレームワーク."""

    practices: tuple[KanbanPractice, ...] = field(default=KANBAN_PRACTICES)
    default_wip_limit: int = 3

    def get_practices_list(self) -> list[str]:
        """プラクティスリストを取得."""
        return [p.name for p in self.practices]


@dataclass
class SAFeFramework:
    """SAFeフレームワーク."""

    levels: tuple[SAFeLevel, ...] = field(default=SAFE_LEVELS)

    def get_level(self, name: str) -> SAFeLevel | None:
        """レベルを名前で取得."""
        for level in self.levels:
            if level.name == name:
                return level
        return None


@dataclass
class AgileFramework:
    """アジャイルフレームワーク統合クラス."""

    scrum: ScrumFramework = field(default_factory=ScrumFramework)
    kanban: KanbanFramework = field(default_factory=KanbanFramework)
    safe: SAFeFramework = field(default_factory=SAFeFramework)

    def get_recommended_sprint_tasks(self) -> list[str]:
        """推奨スプリントタスクを取得."""
        return [
            "Sprint Planning（スプリント計画）",
            "Daily Scrum × スプリント日数",
            "開発作業",
            "Sprint Review（スプリントレビュー）",
            "Sprint Retrospective（振り返り）",
            "Backlog Refinement（バックログリファインメント）",
        ]
