"""Community Feed + Reactions API 스키마 (Backlog-003)."""

from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel, Field, ConfigDict


# --- Feed ---

class FeedItem(BaseModel):
    """피드 항목 (익명, 개인 식별 정보 없음)."""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    record_id: str = Field(..., alias="recordId", description="기록 ID (예: rec_123)")
    created_at: datetime = Field(..., alias="createdAt")
    eaten_at: datetime = Field(..., alias="eatenAt", description="식사일/시간")
    category: Optional[str] = Field(None, alias="category")
    menu_name: Optional[str] = Field(None, alias="menuName")
    reactions: Dict[str, int] = Field(
        default_factory=dict,
        description="코드별 반응 수 예: { \"like\": 3, \"love\": 1, \"yummy\": 5 }",
    )
    my_reaction: Optional[str] = Field(
        None,
        alias="myReaction",
        description="현재 사용자 반응 코드 (비로그인/미반응이면 null)",
    )


class FeedResponse(BaseModel):
    """커뮤니티 피드 응답."""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    items: list[FeedItem] = Field(..., alias="items")
    next_cursor: Optional[str] = Field(None, alias="nextCursor")


# --- Reactions ---

class ReactionRequest(BaseModel):
    """반응 요청 (Backlog-001 코드값)."""

    reaction: str = Field(..., description="like | love | yummy")


class ReactionResponse(BaseModel):
    """반응 등록/변경 응답."""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    record_id: str = Field(..., alias="recordId")
    reaction: str = Field(..., description="적용된 반응 코드")
    result: str = Field(..., description="set | removed | updated")
    counts: Dict[str, int] = Field(..., description="해당 기록의 코드별 반응 수")
