from __future__ import annotations

from typing import Any, Dict, Optional

try:
    from backend.database import db_select_one, db_execute
except Exception:
    from database import db_select_one, db_execute  # type: ignore


def get_job_by_id(job_id: int, user_id: int) -> Optional[Dict[str, Any]]:
    row = db_select_one(
        "SELECT * FROM research_jobs WHERE id = %s AND usuario_id = %s",
        (job_id, user_id),
    )
    return dict(row) if row else None


def save_job_result(job_id: int, result_text: str) -> None:
    db_execute(
        "UPDATE research_jobs SET status = %s, resultado = %s WHERE id = %s",
        ("done", result_text, job_id),
    )

