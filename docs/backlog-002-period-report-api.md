# [Backlog-002] 주/월/연 식습관 리포트 API

## GET /reports/period

기준일이 속한 **주/월/연** 구간의 "내 기록"만 집계해, 카테고리별 비중과 메뉴 빈도 Top N을 반환합니다.

### Request

| Query | 타입 | 필수 | 설명 |
|-------|------|------|------|
| `period` | string | O | `week` \| `month` \| `year` |
| `date` | date | O | 기준일 (YYYY-MM-DD). 이 날이 포함된 기간을 집계 |
| `top_n` | int | X | Top 메뉴 개수 (기본 5, 1~20) |

### Response 200

- `period`: 요청한 period
- `range`: `from`, `to` — 집계 기간 (Backlog-001 규칙: 주=월~일, 월=1일~말일, 연=1/1~12/31)
- `totalRecords`: 기간 내 내 기록 수
- `categoryShare`: `[{ "category", "count", "ratio" }]` — ratio = count / totalRecords
- `topMenus`: `[{ "menuName", "count" }]` — 메뉴명 기준 빈도 내림차순, 최대 top_n개

기록이 없으면 `totalRecords=0`, `categoryShare`/`topMenus`는 빈 배열.

### 에러

- `period`가 `week`/`month`/`year`가 아니면 **400**
- `date` 형식 오류면 **400**
- (권장) 미인증 요청이면 **401**

---

## 호출 예시 (curl)

```bash
# 주간 리포트 (2026-02-24가 속한 주)
curl -s "http://localhost:8000/reports/period?period=week&date=2026-02-24"

# 월간 + Top 10
curl -s "http://localhost:8000/reports/period?period=month&date=2026-02-24&top_n=10"

# 연간
curl -s "http://localhost:8000/reports/period?period=year&date=2026-02-24"
```

(실제 호스트/포트는 서버 설정에 맞게 변경)
