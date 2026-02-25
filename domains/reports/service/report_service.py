"""Reports Service Interface (Backlog-002)."""

from abc import ABC, abstractmethod
from datetime import date

from sqlalchemy.orm import Session

from core.report_period import PeriodType
from domains.reports.schemas import PeriodReportResponse


class ReportServiceInterface(ABC):
    @abstractmethod
    def get_period_report(
        self,
        db: Session,
        user_id: int,
        period: PeriodType,
        reference_date: date,
        top_n: int = 5,
    ) -> PeriodReportResponse:
        """기준일이 속한 주/월/연의 식습관 리포트 조회 (카테고리 비중 + Top 메뉴)."""
        ...
