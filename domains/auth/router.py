"""Kakao 인증 FastAPI 라우터. Controller에만 의존하며 DB 세션은 Depends(get_db)로 주입."""

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from core.database import get_db
from domains.auth.controller.kakao_oauth_controller import KakaoAuthController
from domains.auth.dependencies import get_current_user
from domains.auth.schemas import AuthUserResponse, KakaoUserInfo, OAuthLinkResponse
from domains.auth.service.kakao_oauth_service_impl import KakaoOAuthServiceImpl


def get_controller(db: Session = Depends(get_db)) -> KakaoAuthController:
    """Controller 의존성. Service 구현체와 DB 세션을 주입한다."""
    service = KakaoOAuthServiceImpl()
    return KakaoAuthController(service=service, db=db)


router = APIRouter()


def _login_response_json(data) -> dict:
    """로그인 성공 시 JSON: JWT token + user_info(우리 DB 사용자)."""
    token = {
        "access_token": data.access_token,
        "token_type": data.token_type,
        "expires_in": data.expires_in,
    }
    user = data.user
    user_info = (
        {
            "id": user.id,
            "kakao_id": user.kakao_id,
            "nickname": user.nickname,
            "email": user.email,
            "profile_image_url": user.profile_image_url,
        }
        if user
        else None
    )
    return {"token": token, "user_info": user_info}


@router.get(
    "/request-oauth-link",
    response_class=JSONResponse,
    summary="Kakao 인증 URL 생성",
    description="Kakao OAuth 인증 페이지로 이동할 URL 등을 JSON으로 반환합니다 (PM-JIHYUN-2). auth_url, client_id, redirect_uri, response_type 포함.",
)
def request_oauth_link(
    controller: KakaoAuthController = Depends(get_controller),
):
    """사용자가 Kakao 인증 요청 시 인증 URL 등을 반환한다. 항상 JSON (사진1번 형태)."""
    data = controller.get_oauth_link()
    return JSONResponse(content=data.model_dump())


@router.get(
    "/request-access-token-after-redirection",
    summary="인가 코드로 액세스 토큰 발급",
    description="Kakao 인증 후 전달된 인가 코드로 액세스 토큰 및 사용자 정보를 발급합니다 (PM-JIHYUN-3, PM-JIHYUN-4). JSON으로 token, user_info 반환.",
)
def request_access_token_after_redirection(
    code: str = Query(..., description="Kakao 인증 후 리다이렉트 시 전달된 인가 코드"),
    controller: KakaoAuthController = Depends(get_controller),
):
    """인가 코드(code)를 받아 액세스 토큰 및 사용자 정보를 요청한다. token + user_info 형태 JSON 반환."""
    data = controller.request_access_token_after_redirection(code=code)
    return JSONResponse(content=_login_response_json(data))


@router.get(
    "/user-info",
    response_model=KakaoUserInfo,
    summary="액세스 토큰으로 사용자 정보 조회",
    description="발급받은 Kakao 액세스 토큰으로 사용자 ID, 닉네임, 이메일 등을 조회합니다 (PM-JIHYUN-4).",
)
def get_user_info(
    access_token: str = Query(..., description="Kakao 액세스 토큰"),
    controller: KakaoAuthController = Depends(get_controller),
) -> KakaoUserInfo:
    """발급받은 액세스 토큰으로 Kakao 사용자 정보를 조회한다."""
    return controller.get_user_info(access_token=access_token)


@router.get(
    "/me",
    response_model=AuthUserResponse,
    summary="현재 로그인 사용자 조회",
    description="Authorization: Bearer <JWT> 로 현재 로그인한 우리 DB 사용자 정보를 반환합니다.",
)
def get_me(
    current_user: AuthUserResponse = Depends(get_current_user),
) -> AuthUserResponse:
    """JWT로 인증된 현재 사용자 정보를 반환한다."""
    return current_user
