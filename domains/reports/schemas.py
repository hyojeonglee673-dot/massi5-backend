"""Reports 도메인 요청/응답 스키마 (Backlog-002)."""

from datetime import date
from typing import List

from pydantic import BaseModel, Field, ConfigDict


class PeriodRange(BaseModel):
    """기간 범위 (집계 구간)."""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    from_: date = Field(..., alias="from", description="시작일")
    to: date = Field(..., description="종료일")


class CategoryShareItem(BaseModel):
    """카테고리별 비중."""

    category: str = Field(..., description="카테고리 코드 예: KOREAN, JAPANESE")
    count: int = Field(..., description="해당 카테고리 기록 수")
    ratio: float = Field(..., description="count / totalRecords, 0~1")


class TopMenuItem(BaseModel):
    """최다 빈도 메뉴 항목."""

    menu_name: str = Field(..., alias="menuName", description="메뉴명")
    count: int = Field(..., description="등장 횟수")

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)


class PeriodReportResponse(BaseModel):
    """주/월/연 식습관 리포트 응답 (Backlog-002)."""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    period: str = Field(..., description="week | month | year")
    range: PeriodRange = Field(..., description="집계 기간 from~to")
    total_records: int = Field(..., alias="totalRecords", description="기간 내 내 기록 수")
    category_share: List[CategoryShareItem] = Field(
        ..., alias="categoryShare", description="카테고리별 count·ratio"
    )
    top_menus: List[TopMenuItem] = Field(
        ..., alias="topMenus", description="메뉴명 기준 빈도 Top N"
    )


# --- 하위 호환용 (기존 start_date/end_date 방식 사용 시) ---


class ReportSummary(BaseModel):
    """리포트 요약 (기간별 점심 기록 수 등)."""

    start_date: date
    end_date: date
    total_records: int = Field(..., description="기간 내 점심 기록 수")


class ReportResponse(BaseModel):
    """리포트 응답 (레거시)."""

    summary: ReportSummary
