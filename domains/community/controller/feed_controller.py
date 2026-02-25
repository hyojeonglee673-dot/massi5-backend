"""Community Feed Controller (Backlog-003)."""

from typing import Optional

from sqlalchemy.orm import Session

from domains.community.schemas import FeedResponse, ReactionResponse
from domains.community.service.feed_service import FeedServiceInterface


class FeedController:
    def __init__(self, service: FeedServiceInterface, db: Session) -> None:
        self._service = service
        self._db = db

    def get_feed(
        self,
        category: Optional[str],
        limit: int,
        cursor: Optional[str],
        current_user_id: Optional[int],
    ) -> FeedResponse:
        return self._service.get_feed(
            self._db,
            category=category,
            limit=limit,
            cursor=cursor,
            current_user_id=current_user_id,
        )

    def set_reaction(self, record_id: int, user_id: int, reaction: str) -> ReactionResponse:
        return self._service.set_reaction(
            self._db,
            record_id=record_id,
            user_id=user_id,
            reaction=reaction,
        )
