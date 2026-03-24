"""DevPilot データベース.

SQLAlchemy + aiosqlite によるプロジェクトデータ永続化。
"""

from __future__ import annotations

import json
from datetime import date, datetime
from typing import Any

from sqlalchemy import Column, DateTime, Float, Integer, String, Text, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

Base = declarative_base()

DEFAULT_DATABASE_URL = "sqlite:///./devpilot.db"


class ProjectRecord(Base):  # type: ignore[misc]
    """プロジェクトレコード."""

    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=False)
    project_type = Column(String(50), nullable=False)
    methodology = Column(String(50), nullable=False)
    start_date = Column(String(10), nullable=False)
    target_end_date = Column(String(10), nullable=False)
    team_size = Column(Integer, nullable=False)
    budget_jpy = Column(Integer, nullable=True)
    plan_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class RiskRecord(Base):  # type: ignore[misc]
    """リスクレコード."""

    __tablename__ = "risks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, nullable=False, index=True)
    risk_id = Column(String(50), nullable=False)
    category = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    probability = Column(Float, nullable=False)
    impact = Column(Float, nullable=False)
    risk_score = Column(Float, nullable=False)
    level = Column(String(20), nullable=False)
    mitigation = Column(Text, nullable=False)
    contingency = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class ReportRecord(Base):  # type: ignore[misc]
    """レポートレコード."""

    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, nullable=False, index=True)
    report_date = Column(String(10), nullable=False)
    report_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Database:
    """データベース管理クラス."""

    def __init__(self, database_url: str = DEFAULT_DATABASE_URL) -> None:
        self.engine = create_engine(database_url, echo=False)
        self.session_factory = sessionmaker(bind=self.engine)

    def create_tables(self) -> None:
        """テーブル作成."""
        Base.metadata.create_all(self.engine)

    def get_session(self) -> Session:
        """セッション取得."""
        return self.session_factory()

    def save_project(self, project_data: dict[str, Any]) -> int:
        """プロジェクト保存."""
        with self.get_session() as session:
            record = ProjectRecord(
                name=project_data["name"],
                description=project_data["description"],
                project_type=project_data["project_type"],
                methodology=project_data["methodology"],
                start_date=str(project_data["start_date"]),
                target_end_date=str(project_data["target_end_date"]),
                team_size=project_data["team_size"],
                budget_jpy=project_data.get("budget_jpy"),
                plan_json=json.dumps(
                    project_data.get("plan"), ensure_ascii=False, default=str,
                ),
            )
            session.add(record)
            session.commit()
            session.refresh(record)
            return int(record.id)

    def get_project(self, project_id: int) -> dict[str, Any] | None:
        """プロジェクト取得."""
        with self.get_session() as session:
            record = session.query(ProjectRecord).filter_by(id=project_id).first()
            if record is None:
                return None
            return {
                "id": record.id,
                "name": record.name,
                "description": record.description,
                "project_type": record.project_type,
                "methodology": record.methodology,
                "start_date": record.start_date,
                "target_end_date": record.target_end_date,
                "team_size": record.team_size,
                "budget_jpy": record.budget_jpy,
                "plan": json.loads(record.plan_json) if record.plan_json else None,
            }

    def list_projects(self) -> list[dict[str, Any]]:
        """プロジェクト一覧."""
        with self.get_session() as session:
            records = session.query(ProjectRecord).all()
            return [
                {
                    "id": r.id,
                    "name": r.name,
                    "project_type": r.project_type,
                    "start_date": r.start_date,
                    "target_end_date": r.target_end_date,
                }
                for r in records
            ]

    def save_report(
        self, project_id: int, report_date: date, report_data: dict[str, Any],
    ) -> int:
        """レポート保存."""
        with self.get_session() as session:
            record = ReportRecord(
                project_id=project_id,
                report_date=str(report_date),
                report_json=json.dumps(report_data, ensure_ascii=False, default=str),
            )
            session.add(record)
            session.commit()
            session.refresh(record)
            return int(record.id)
