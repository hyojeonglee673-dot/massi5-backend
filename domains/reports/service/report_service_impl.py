"""Reports Service 구현체 (Backlog-002)."""

from datetime import date
from typing import List

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from core.report_period import PeriodType, get_period_range
from domains.reports.schemas import (
    CategoryShareItem,
    PeriodRange,
    PeriodReportResponse,
    TopMenuItem,
)
from domains.reports.service.report_service import ReportServiceInterface
from models import LunchRecord


class ReportServiceImpl(ReportServiceInterface):
    def get_period_report(
        self,
        db: Session,
        user_id: int,
        period: PeriodType,
        reference_date: date,
        top_n: int = 5,
    ) -> PeriodReportResponse:
        from_date, to_date = get_period_range(reference_date, period)

        # 전체 기록 수 (기간 내 내 기록)
        count_stmt = (
            select(func.count(LunchRecord.id))
            .where(LunchRecord.user_id == user_id)
            .where(LunchRecord.recorded_at >= from_date)
            .where(LunchRecord.recorded_at <= to_date)
        )
        total_records = db.scalar(count_stmt) or 0

        category_share: List[CategoryShareItem] = []
        top_menus: List[TopMenuItem] = []

        if total_records > 0:
            # 카테고리별 집계 (category가 있는 기록만)
            cat_stmt = (
                select(LunchRecord.category, func.count(LunchRecord.id))
                .where(LunchRecord.user_id == user_id)
                .where(LunchRecord.recorded_at >= from_date)
                .where(LunchRecord.recorded_at <= to_date)
                .where(LunchRecord.category.isnot(None))
                .where(LunchRecord.category != "")
                .group_by(LunchRecord.category)
            )
            rows = db.execute(cat_stmt).all()
            for category, count in rows:
                ratio = round(count / total_records, 4)
                category_share.append(
                    CategoryShareItem(category=category, count=count, ratio=ratio)
                )
            # ratio 합계 ≈ 1 되도록 정렬 후 유지 (반올림 오차 허용)

            # 메뉴명별 빈도 Top N (menu_name이 있는 기록만)
            menu_stmt = (
                select(LunchRecord.menu_name, func.count(LunchRecord.id))
                .where(LunchRecord.user_id == user_id)
                .where(LunchRecord.recorded_at >= from_date)
                .where(LunchRecord.recorded_at <= to_date)
                .where(LunchRecord.menu_name.isnot(None))
                .where(LunchRecord.menu_name != "")
                .group_by(LunchRecord.menu_name)
                .order_by(func.count(LunchRecord.id).desc())
                .limit(top_n)
            )
            menu_rows = db.execute(menu_stmt).all()
            top_menus = [
                TopMenuItem(menu_name=name, count=cnt) for name, cnt in menu_rows
            ]

        return PeriodReportResponse(
            period=period,
            range=PeriodRange(from_=from_date, to=to_date),
            total_records=total_records,
            category_share=category_share,
            top_menus=top_menus,
        )
