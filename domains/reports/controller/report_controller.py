"""Reports Controller (Backlog-002)."""

from datetime import date

from sqlalchemy.orm import Session

from core.report_period import PERIOD_TYPES, PeriodType
from domains.reports.schemas import PeriodReportResponse
from domains.reports.service.report_service import ReportServiceInterface


class ReportController:
    def __init__(self, service: ReportServiceInterface, db: Session) -> None:
        self._service = service
        self._db = db

    def get_period_report(
        self,
        user_id: int,
        period: PeriodType,
        reference_date: date,
        top_n: int = 5,
    ) -> PeriodReportResponse:
        """기준일이 속한 주/월/연 식습관 리포트 조회."""
        return self._service.get_period_report(
            self._db,
            user_id=user_id,
            period=period,
            reference_date=reference_date,
            top_n=top_n,
        )
