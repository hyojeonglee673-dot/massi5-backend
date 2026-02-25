"""Community Feed Service 구현체 (Backlog-003)."""

from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from core.reactions import ALLOWED_REACTION_CODES
from domains.community.schemas import FeedItem, FeedResponse, ReactionResponse
from domains.community.service.feed_service import FeedServiceInterface
from models import LunchRecord
from models.community import Reaction


def _record_id_str(pk: int) -> str:
    return f"rec_{pk}"


def _default_counts() -> Dict[str, int]:
    return {code: 0 for code in ALLOWED_REACTION_CODES}


class FeedServiceImpl(FeedServiceInterface):
    def get_feed(
        self,
        db: Session,
        category: Optional[str],
        limit: int,
        cursor: Optional[str],
        current_user_id: Optional[int],
    ) -> FeedResponse:
        # Cursor: last seen record id (exclusive). Order by id DESC.
        stmt = (
            select(LunchRecord)
            .order_by(LunchRecord.id.desc())
            .limit(limit + 1)
        )
        if category is not None and category != "":
            stmt = stmt.where(LunchRecord.category == category)
        if cursor is not None and cursor != "":
            try:
                cursor_id = int(cursor)
                stmt = stmt.where(LunchRecord.id < cursor_id)
            except ValueError:
                pass
        rows = db.execute(stmt).scalars().all()
        has_more = len(rows) > limit
        records = list(rows[:limit])
        next_cursor = str(records[-1].id) if has_more and records else None

        if not records:
            return FeedResponse(items=[], next_cursor=None)

        record_ids = [r.id for r in records]

        # Reaction counts per record: { record_id: { "like": n, "love": n, "yummy": n } }
        count_stmt = (
            select(Reaction.lunch_record_id, Reaction.reaction_type, func.count(Reaction.id))
            .where(Reaction.lunch_record_id.in_(record_ids))
            .where(Reaction.reaction_type.in_(ALLOWED_REACTION_CODES))
            .group_by(Reaction.lunch_record_id, Reaction.reaction_type)
        )
        count_rows = db.execute(count_stmt).all()
        counts_by_record: Dict[int, Dict[str, int]] = {}
        for rid in record_ids:
            counts_by_record[rid] = _default_counts().copy()
        for rid, rtype, cnt in count_rows:
            if rtype in ALLOWED_REACTION_CODES:
                counts_by_record[rid][rtype] = cnt

        # Current user's reaction per record
        my_reactions: Dict[int, str] = {}
        if current_user_id is not None:
            my_stmt = (
                select(Reaction.lunch_record_id, Reaction.reaction_type)
                .where(Reaction.lunch_record_id.in_(record_ids))
                .where(Reaction.user_id == current_user_id)
            )
            for rid, rtype in db.execute(my_stmt).all():
                my_reactions[rid] = rtype

        # Build items (anonymous: no user_id)
        tz = timezone(offset=timedelta(hours=9))
        items: List[FeedItem] = []
        for r in records:
            eaten_at = datetime.combine(r.recorded_at, datetime.min.time()).replace(tzinfo=tz)
            created_at = r.created_at
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)
            items.append(
                FeedItem(
                    record_id=_record_id_str(r.id),
                    created_at=created_at,
                    eaten_at=eaten_at,
                    category=r.category,
                    menu_name=r.menu_name,
                    reactions=counts_by_record.get(r.id, _default_counts()),
                    my_reaction=my_reactions.get(r.id),
                )
            )
        return FeedResponse(items=items, next_cursor=next_cursor)

    def set_reaction(
        self,
        db: Session,
        record_id: int,
        user_id: int,
        reaction: str,
    ) -> ReactionResponse:
        # Check record exists
        record = db.get(LunchRecord, record_id)
        if record is None:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Record not found")

        existing = (
            db.execute(
                select(Reaction)
                .where(Reaction.lunch_record_id == record_id)
                .where(Reaction.user_id == user_id)
            )
        ).scalars().first()

        if existing is None:
            db.add(Reaction(lunch_record_id=record_id, user_id=user_id, reaction_type=reaction))
            db.commit()
            result = "set"
        elif existing.reaction_type == reaction:
            # Toggle: remove
            db.delete(existing)
            db.commit()
            result = "removed"
        else:
            existing.reaction_type = reaction
            db.add(existing)
            db.commit()
            result = "updated"

        # Current counts for this record
        count_stmt = (
            select(Reaction.reaction_type, func.count(Reaction.id))
            .where(Reaction.lunch_record_id == record_id)
            .where(Reaction.reaction_type.in_(ALLOWED_REACTION_CODES))
            .group_by(Reaction.reaction_type)
        )
        count_rows = db.execute(count_stmt).all()
        counts = _default_counts().copy()
        for rtype, cnt in count_rows:
            counts[rtype] = cnt

        return ReactionResponse(
            record_id=_record_id_str(record_id),
            reaction=reaction,
            result=result,
            counts=counts,
        )
