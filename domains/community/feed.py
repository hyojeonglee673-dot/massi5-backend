"""
커뮤니티 피드 + 반응 API (Backlog-003).

파일명: feed
- GET /community/feed: 익명 피드 (카테고리/커서/limit)
- POST /records/{record_id}/reactions: 반응 남기기/토글
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from core.database import get_db
from core.reactions import is_allowed_reaction_code
from domains.community.controller.feed_controller import FeedController
from domains.community.schemas import FeedResponse, ReactionRequest, ReactionResponse
from domains.community.service.feed_service_impl import FeedServiceImpl


def get_feed_controller(db: Session = Depends(get_db)) -> FeedController:
    return FeedController(service=FeedServiceImpl(), db=db)


# GET /community/feed → prefix "/community" 로 마운트
feed_router = APIRouter()


@feed_router.get(
    "/feed",
    response_model=FeedResponse,
    summary="커뮤니티 피드",
    description="전체 사용자의 최신 기록을 익명 피드로 반환. userId/닉네임 등 개인 식별 정보 없음.",
)
def get_feed(
    category: Optional[str] = Query(None, description="음식 카테고리 필터 (예: KOREAN)"),
    limit: int = Query(20, ge=1, le=50, description="페이지당 개수"),
    cursor: Optional[str] = Query(None, description="다음 페이지 커서 (없으면 첫 페이지)"),
    controller: FeedController = Depends(get_feed_controller),
    # TODO: 인증 시 user_id 주입, 비로그인 허용 시 None
    user_id: Optional[int] = 1,
) -> FeedResponse:
    return controller.get_feed(
        category=category,
        limit=limit,
        cursor=cursor,
        current_user_id=user_id,
    )


# POST /records/{record_id}/reactions → prefix 없이 마운트
reactions_router = APIRouter()


@reactions_router.post(
    "/records/{record_id}/reactions",
    response_model=ReactionResponse,
    summary="반응 남기기/토글",
    description="허용 코드: like, love, yummy. 동일 반응 재요청 시 제거(removed).",
    responses={400: {"description": "reaction 코드 오류"}, 401: {"description": "미인증"}, 404: {"description": "기록 없음"}},
)
def post_reaction(
    record_id: int,
    body: ReactionRequest,
    controller: FeedController = Depends(get_feed_controller),
    # TODO: 인증 필수 시 미인증이면 401
    user_id: int = 1,
) -> ReactionResponse:
    if not is_allowed_reaction_code(body.reaction):
        raise HTTPException(status_code=400, detail=f"Invalid reaction. Allowed: like, love, yummy")
    return controller.set_reaction(record_id=record_id, user_id=user_id, reaction=body.reaction)
