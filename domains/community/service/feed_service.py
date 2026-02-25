"""Community Feed Service Interface (Backlog-003)."""

from abc import ABC, abstractmethod
from typing import Optional

from sqlalchemy.orm import Session

from domains.community.schemas import FeedResponse, ReactionResponse


class FeedServiceInterface(ABC):
    @abstractmethod
    def get_feed(
        self,
        db: Session,
        category: Optional[str],
        limit: int,
        cursor: Optional[str],
        current_user_id: Optional[int],
    ) -> FeedResponse:
        """커뮤니티 피드 조회 (익명, 카테고리/커서/limit)."""
        ...

    @abstractmethod
    def set_reaction(
        self,
        db: Session,
        record_id: int,
        user_id: int,
        reaction: str,
    ) -> ReactionResponse:
        """반응 설정/토글 (Backlog-001 정책: 1인 1기록당 1타입, 토글 시 removed)."""
        ...
