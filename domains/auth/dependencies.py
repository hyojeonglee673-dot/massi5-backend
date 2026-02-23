"""Auth 도메인 의존성: JWT 검증 및 현재 사용자 조회."""

import os
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from core.database import get_db
from domains.auth.schemas import AuthUserResponse
from models.user import User

HTTPBearerScheme = HTTPBearer(auto_error=False)
JWT_ALGORITHM = "HS256"


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(HTTPBearerScheme)],
    db: Annotated[Session, Depends(get_db)],
) -> AuthUserResponse:
    """Authorization: Bearer <JWT> 에서 사용자 ID를 꺼내 DB에서 조회 후 반환. 실패 시 401."""
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증이 필요합니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    secret = os.getenv("JWT_SECRET_KEY", "")
    if not secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="JWT 설정이 없습니다.",
        )
    try:
        payload = jwt.decode(
            credentials.credentials,
            secret,
            algorithms=[JWT_ALGORITHM],
        )
        user_id_str = payload.get("sub")
        if not user_id_str:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="잘못된 토큰입니다.")
        user_id = int(user_id_str)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰이 만료되었습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except (jwt.InvalidTokenError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="잘못된 토큰입니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="사용자를 찾을 수 없습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return AuthUserResponse(
        id=user.id,
        kakao_id=user.kakao_id,
        nickname=user.nickname,
        email=user.email,
        profile_image_url=user.profile_image_url,
    )
