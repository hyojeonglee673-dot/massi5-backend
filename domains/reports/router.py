"""Reports FastAPI 라우터 (Backlog-002)."""

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from core.database import get_db
from core.report_period import PeriodType
from domains.reports.controller.report_controller import ReportController
from domains.reports.schemas import PeriodReportResponse
from domains.reports.service.report_service_impl import ReportServiceImpl


def get_controller(db: Session = Depends(get_db)) -> ReportController:
    """Controller 의존성."""
    return ReportController(service=ReportServiceImpl(), db=db)


router = APIRouter()


@router.get(
    "/period",
    response_model=PeriodReportResponse,
    summary="주/월/연 식습관 리포트",
    description="기준일이 속한 주/월/연의 카테고리별 비중과 Top 메뉴를 반환합니다.",
    responses={
        200: {"description": "리포트 (기록 없으면 totalRecords=0, 빈 배열)"},
        400: {"description": "period 또는 date 형식 오류"},
    },
)
def get_period_report(
    period: PeriodType = Query(..., description="week | month | year"),
    date_param: date = Query(..., alias="date", description="기준일 (YYYY-MM-DD)"),
    top_n: int = Query(5, ge=1, le=20, description="Top 메뉴 개수"),
    controller: ReportController = Depends(get_controller),
    # TODO: 인증 후 user_id는 JWT 등에서 추출, 미인증 시 401
    user_id: int = 1,
) -> PeriodReportResponse:
    """기준일이 포함된 기간의 내 기록만 집계: 카테고리 비중 + 메뉴 빈도 Top N."""
    return controller.get_period_report(
        user_id=user_id,
        period=period,
        reference_date=date_param,
        top_n=top_n,
    )
