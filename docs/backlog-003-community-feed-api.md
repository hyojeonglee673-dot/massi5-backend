# [Backlog-003] 커뮤니티 피드 + 반응 API

## API 1) 커뮤니티 피드

### GET /community/feed

| Query | 타입 | 필수 | 설명 |
|-------|------|------|------|
| `category` | string | X | 음식 카테고리 필터 (예: KOREAN) |
| `limit` | int | X | 기본 20, 최대 50 |
| `cursor` | string | X | 페이지네이션 (없으면 첫 페이지) |

**응답**: `items[]` (recordId, createdAt, eatenAt, category, menuName, reactions, myReaction), `nextCursor`.

- **익명**: userId, 닉네임, 위치 등 개인 식별 정보 미포함.
- **reactions**: `{ "like": n, "love": n, "yummy": n }`.
- **myReaction**: 로그인 사용자 기준 (비로그인/미반응이면 null).

---

## API 2) 반응 남기기

### POST /records/{id}/reactions

**Body**: `{ "reaction": "yummy" }` (Backlog-001 코드값: like | love | yummy)

**응답**: `recordId`, `reaction`, `result` (set | removed | updated), `counts`.

- **정책(Backlog-001)**: 동일 사용자·동일 기록에 반응 1개. 같은 반응 재요청 시 **토글(removed)**.
- 허용되지 않은 reaction 코드면 **400**. 기록 없으면 **404**. (권장) 미인증 **401**.

---

## 완료 조건

- [x] /community/feed에서 최신 기록이 limit만큼 내려온다.
- [x] category 필터 동작.
- [x] cursor 기반 페이지네이션 (id DESC, cursor 미지정 시 첫 페이지).
- [x] /records/{id}/reactions로 허용된 reaction만 저장 (그 외 400).
- [x] 피드 응답에 반응 카운트 포함.
- [x] 개인 식별 정보 미포함.

## Out of Scope

- 신고/차단/모더레이션, 인기글 랭킹, 댓글
