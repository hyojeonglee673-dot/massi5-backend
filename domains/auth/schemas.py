"""Kakao 인증 관련 요청/응답 스키마."""

from typing import Optional

from pydantic import BaseModel, Field


# --- PM-JIHYUN-2: 인증 URL ---
class OAuthLinkResponse(BaseModel):
    """인증 URL 생성 API 응답 (사진1번 형태: auth_url, client_id, redirect_uri, response_type)."""
    auth_url: str = Field(..., description="Kakao OAuth 인증 페이지 URL")
    client_id: str = Field(..., description="Kakao REST API 키")
    redirect_uri: str = Field(..., description="로그인 후 리다이렉트될 콜백 URL")
    response_type: str = Field(default="code", description="OAuth response_type")


# --- PM-JIHYUN-3, PM-JIHYUN-4: 토큰 및 사용자 정보 ---
class KakaoUserInfo(BaseModel):
    """Kakao 사용자 정보 (PM-JIHYUN-4)."""
    id: int = Field(..., description="Kakao 사용자 ID")
    nickname: Optional[str] = Field(None, description="닉네임")
    email: Optional[str] = Field(None, description="이메일 (동의 시)")
    profile_image_url: Optional[str] = Field(None, description="프로필 이미지 URL")


class AuthUserResponse(BaseModel):
    """로그인 성공 시 반환하는 우리 DB 사용자 정보 (JWT 인증용)."""
    id: int = Field(..., description="우리 DB 사용자 ID")
    kakao_id: int = Field(..., description="Kakao 사용자 ID")
    nickname: Optional[str] = Field(None, description="닉네임")
    email: Optional[str] = Field(None, description="이메일")
    profile_image_url: Optional[str] = Field(None, description="프로필 이미지 URL")


class AccessTokenResponse(BaseModel):
    """로그인 성공 API 응답. JWT(access_token) + 우리 DB 사용자 정보."""
    access_token: str = Field(..., description="JWT 액세스 토큰")
    token_type: str = Field(default="bearer", description="토큰 타입")
    expires_in: Optional[int] = Field(None, description="JWT 만료 시간(초)")
    user: Optional[AuthUserResponse] = Field(None, description="우리 DB 사용자 정보")
