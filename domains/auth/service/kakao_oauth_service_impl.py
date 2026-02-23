"""Kakao OAuth Service 구현체. 환경 변수(.env) 기반 설정, DB 사용자 조회/생성, JWT 발급.

필요 환경 변수 (애플리케이션 시작 시 load_env()로 .env에서 로드됨):
- KAKAO_CLIENT_ID, KAKAO_REDIRECT_URI, KAKAO_CLIENT_SECRET (Kakao OAuth)
- JWT_SECRET_KEY (필수, JWT 서명용 비밀키)
- JWT_EXPIRE_MINUTES (선택, 기본 60)
"""

import os
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

import httpx
import jwt
from sqlalchemy.orm import Session
from sqlmodel import select

from domains.auth.schemas import (
    AccessTokenResponse,
    AuthUserResponse,
    KakaoUserInfo,
    OAuthLinkResponse,
)
from domains.auth.service.kakao_oauth_service import KakaoAuthServiceInterface
from models.user import User

# Kakao OAuth 상수 (엔드포인트 URL만 하드코딩)
KAKAO_AUTH_URL = "https://kauth.kakao.com/oauth/authorize"
KAKAO_TOKEN_URL = "https://kauth.kakao.com/oauth/token"
KAKAO_USER_ME_URL = "https://kapi.kakao.com/v2/user/me"

# JWT: .env에서 JWT_SECRET_KEY, JWT_ALGORITHM(기본 HS256), JWT_EXPIRE_MINUTES 로드
JWT_ALGORITHM = "HS256"


class KakaoOAuthServiceImpl(KakaoAuthServiceInterface):
    """Kakao OAuth 서비스 구현체. client_id, redirect_uri, client_secret, JWT 설정은 환경 변수에서 로드."""

    def __init__(self) -> None:
        self._client_id = os.getenv("KAKAO_CLIENT_ID")
        self._redirect_uri = os.getenv("KAKAO_REDIRECT_URI")
        self._client_secret = os.getenv("KAKAO_CLIENT_SECRET")
        self._jwt_secret = os.getenv("JWT_SECRET_KEY", "")
        self._jwt_expire_minutes = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))

    def _validate_oauth_config(self) -> None:
        """OAuth 필수 설정값 검증. 누락 시 예외."""
        if not self._client_id:
            raise ValueError("KAKAO_CLIENT_ID가 설정되지 않았습니다.")
        if not self._redirect_uri:
            raise ValueError("KAKAO_REDIRECT_URI가 설정되지 않았습니다.")

    def _validate_jwt_config(self) -> None:
        """JWT 필수 설정값 검증."""
        if not self._jwt_secret:
            raise ValueError("JWT_SECRET_KEY가 설정되지 않았습니다.")

    def _find_or_create_user(
        self,
        db: Session,
        kakao_id: int,
        nickname: str | None,
        email: str | None,
        profile_image_url: str | None,
    ) -> User:
        """kakao_id로 사용자 조회. 없으면 새로 생성 후 반환."""
        stmt = select(User).where(User.kakao_id == kakao_id)
        user = db.execute(stmt).scalars().first()
        if user:
            return user
        user = User(
            kakao_id=kakao_id,
            nickname=nickname,
            email=email,
            profile_image_url=profile_image_url,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def _create_jwt(self, user_id: int) -> tuple[str, int]:
        """우리 DB user_id로 JWT 생성. (token, expires_in_seconds) 반환."""
        self._validate_jwt_config()
        expires = datetime.now(timezone.utc) + timedelta(minutes=self._jwt_expire_minutes)
        payload = {"sub": str(user_id), "exp": expires}
        token = jwt.encode(
            payload,
            self._jwt_secret,
            algorithm=JWT_ALGORITHM,
        )
        if isinstance(token, bytes):
            token = token.decode("utf-8")
        return token, self._jwt_expire_minutes * 60

    def get_authorization_url(self) -> OAuthLinkResponse:
        """Kakao OAuth 인증 URL 생성 (PM-JIHYUN-2). client_id, redirect_uri, response_type 포함."""
        self._validate_oauth_config()
        params = {
            "client_id": self._client_id,
            "redirect_uri": self._redirect_uri,
            "response_type": "code",
        }
        auth_url = f"{KAKAO_AUTH_URL}?{urlencode(params)}"
        return OAuthLinkResponse(
            auth_url=auth_url,
            client_id=self._client_id,
            redirect_uri=self._redirect_uri,
            response_type="code",
        )

    def request_access_token(self, code: str, db: Session) -> AccessTokenResponse:
        """인가 코드로 Kakao 토큰·사용자 조회 → DB에 사용자 저장/조회 → JWT 발급 후 반환."""
        self._validate_oauth_config()
        if not self._client_secret:
            raise ValueError("KAKAO_CLIENT_SECRET이 설정되지 않았습니다.")
        if not code or not code.strip():
            raise ValueError("인가 코드(code)가 필요합니다.")

        data = {
            "grant_type": "authorization_code",
            "client_id": self._client_id,
            "redirect_uri": self._redirect_uri,
            "code": code.strip(),
            "client_secret": self._client_secret,
        }

        with httpx.Client() as client:
            token_res = client.post(
                KAKAO_TOKEN_URL,
                headers={"Content-Type": "application/x-www-form-urlencoded;charset=utf-8"},
                data=data,
            )
            token_res.raise_for_status()
            token_body = token_res.json()

        access_token = token_body.get("access_token")
        if not access_token:
            raise ValueError("액세스 토큰을 받지 못했습니다.")

        kakao_user = self.get_user_info(access_token)
        user = self._find_or_create_user(
            db,
            kakao_id=kakao_user.id,
            nickname=kakao_user.nickname,
            email=kakao_user.email,
            profile_image_url=kakao_user.profile_image_url,
        )
        jwt_token, expires_in = self._create_jwt(user.id)

        return AccessTokenResponse(
            access_token=jwt_token,
            token_type="bearer",
            expires_in=expires_in,
            user=AuthUserResponse(
                id=user.id,
                kakao_id=user.kakao_id,
                nickname=user.nickname,
                email=user.email,
                profile_image_url=user.profile_image_url,
            ),
        )

    def get_user_info(self, access_token: str) -> KakaoUserInfo:
        """액세스 토큰으로 Kakao 사용자 정보 조회 (PM-JIHYUN-4)."""
        if not access_token or not access_token.strip():
            raise ValueError("액세스 토큰이 필요합니다.")

        with httpx.Client() as client:
            res = client.get(
                KAKAO_USER_ME_URL,
                headers={
                    "Authorization": f"Bearer {access_token.strip()}",
                    "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
                },
            )
            res.raise_for_status()
            body = res.json()

        kakao_account = body.get("kakao_account") or {}
        profile = kakao_account.get("profile") or {}
        return KakaoUserInfo(
            id=body.get("id"),
            nickname=profile.get("nickname"),
            email=kakao_account.get("email"),
            profile_image_url=profile.get("profile_image_url"),
        )
