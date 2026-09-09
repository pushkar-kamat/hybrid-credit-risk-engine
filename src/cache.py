import hashlib
import json
import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
CACHE_DB = BASE_DIR / "memo_cache.db"


def initialize_cache():
    try:
        with sqlite3.connect(CACHE_DB) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS memo_cache (
                    applicant_key TEXT PRIMARY KEY,
                    memo TEXT NOT NULL
                )
                """
            )
            conn.commit()

    except sqlite3.Error as e:
        raise RuntimeError(
            f"Failed to initialize memo cache: {e}"
        ) from e


def create_applicant_key(applicant: dict) -> str:
    """
    Create a stable hash from applicant data.

    Same applicant data -> same key.
    Different applicant data -> different key.
    """

    try:
        normalized = json.dumps(
            applicant,
            sort_keys=True,
            default=str
        )

        return hashlib.sha256(
            normalized.encode("utf-8")
        ).hexdigest()

    except (TypeError, ValueError) as e:
        raise ValueError(
            f"Failed to create applicant cache key: {e}"
        ) from e


def get_cached_memo(applicant_key: str):
    try:
        with sqlite3.connect(CACHE_DB) as conn:
            row = conn.execute(
                """
                SELECT memo
                FROM memo_cache
                WHERE applicant_key = ?
                """,
                (applicant_key,)
            ).fetchone()

        return row[0] if row else None

    except sqlite3.Error as e:
        raise RuntimeError(
            f"Failed to read memo cache: {e}"
        ) from e


def save_cached_memo(applicant_key: str, memo: str):
    try:
        with sqlite3.connect(CACHE_DB) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO memo_cache
                (applicant_key, memo)
                VALUES (?, ?)
                """,
                (applicant_key, memo)
            )
            conn.commit()

    except sqlite3.Error as e:
        raise RuntimeError(
            f"Failed to save memo to cache: {e}"
        ) from e