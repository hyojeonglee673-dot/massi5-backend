"""Reaction 테이블 (점심 기록에 대한 반응)."""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Reaction(SQLModel, table=True):
    """점심 기록에 대한 반응 (좋아요 등).

    규격: docs/backlog-001-report-period-and-reactions.md §3
    - reaction_type: 허용 코드값만 사용 (core.reactions.ALLOWED_REACTION_CODES).
    - 동일 (lunch_record_id, user_id, reaction_type) 중복 불가 — 업서트/유니크 제약 권장.
    """

    __tablename__ = "reactions"

    id: Optional[int] = Field(default=None, primary_key=True)
    lunch_record_id: int = Field(foreign_key="lunch_records.id", index=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    reaction_type: str = Field(max_length=50, description="코드값: like, love, yummy (Backlog-001)")
    created_at: datetime = Field(default_factory=datetime.utcnow)
