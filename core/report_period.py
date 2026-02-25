"""
리포트 집계 기간 규격 (Backlog-001).

- 기간 계산 규칙: docs/backlog-001-report-period-and-reactions.md §2 참조.
- 주(week): ISO-8601 기준, 월요일 시작.
"""

from datetime import date, timedelta
from typing import Literal, Tuple

# API에서 사용하는 period 파라미터 값
PeriodType = Literal["week", "month", "year"]
PERIOD_TYPES: tuple[PeriodType, ...] = ("week", "month", "year")

# 주의 시작 요일 (문서와 일치)
WEEK_START = "monday"  # ISO-8601

# 기본 타임존 (사용자 타임존 미설정 시)
DEFAULT_TIMEZONE = "Asia/Seoul"


def get_period_range(reference_date: date, period: PeriodType) -> Tuple[date, date]:
    """기준일이 속한 주/월/연의 시작일·종료일을 반환 (Backlog-001 §2).

    - week: 해당 주 월요일 ~ 일요일 (ISO-8601)
    - month: 해당 월 1일 ~ 말일
    - year: 1월 1일 ~ 12월 31일
    """
    if period == "week":
        # Python weekday(): Monday=0, Sunday=6
        monday = reference_date - timedelta(days=reference_date.weekday())
        sunday = monday + timedelta(days=6)
        return (monday, sunday)
    if period == "month":
        first = reference_date.replace(day=1)
        # 다음 달 1일 - 1일 = 이번 달 말일
        if reference_date.month == 12:
            next_first = reference_date.replace(year=reference_date.year + 1, month=1, day=1)
        else:
            next_first = reference_date.replace(month=reference_date.month + 1, day=1)
        last = next_first - timedelta(days=1)
        return (first, last)
    if period == "year":
        return (
            reference_date.replace(month=1, day=1),
            reference_date.replace(month=12, day=31),
        )
    raise ValueError(f"Invalid period: {period}")
