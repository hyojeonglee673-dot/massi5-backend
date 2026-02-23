"""Kakao 인증 Service Interface. Controller는 이 인터페이스에만 의존한다."""

from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from domains.auth.schemas import AccessTokenResponse, KakaoUserInfo, OAuthLinkResponse


class KakaoAuthServiceInterface(ABC):
    """Kakao OAuth 인증 서비스 인터페이스. 구현체에 직접 의존하지 않는다."""

    @abstractmethod
    def get_authorization_url(self) -> OAuthLinkResponse:
        """Kakao OAuth 인증 URL을 생성하여 반환한다 (PM-JIHYUN-2)."""
        ...

    @abstractmethod
    def request_access_token(self, code: str, db: Session) -> AccessTokenResponse:
        """인가 코드로 Kakao 토큰·사용자 조회 후, DB에 사용자 저장/조회하고 JWT 및 우리 사용자 정보를 반환한다."""
        ...

    @abstractmethod
    def get_user_info(self, access_token: str) -> KakaoUserInfo:
        """액세스 토큰으로 Kakao 사용자 정보를 조회한다 (PM-JIHYUN-4)."""
        ...
