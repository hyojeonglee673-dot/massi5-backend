"""
커뮤니티 반응(이모지) 규격 (Backlog-001).

- 허용 종류·저장 방식·중복 정책: docs/backlog-001-report-period-and-reactions.md §3 참조.
- 저장은 코드값만 사용; 표시 시 아래 매핑으로 이모지 렌더링.
"""

from typing import Dict

# 허용 반응 코드값 (DB/API 저장용)
ALLOWED_REACTION_CODES = ("like", "love", "yummy")

# 코드값 → 표시 이모지 (클라이언트 매핑용)
REACTION_CODE_TO_EMOJI: Dict[str, str] = {
    "like": "👍",
    "love": "❤️",
    "yummy": "😋",
}


def is_allowed_reaction_code(code: str) -> bool:
    """code가 허용된 반응 코드인지 확인."""
    return code in ALLOWED_REACTION_CODES
