from __future__ import annotations

import json
import os
import sqlite3
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken

from .models import AnalysisResult, Finding, HistoryEntry


def default_data_dir() -> Path:
    base = os.environ.get("LOCALAPPDATA")
    if base:
        return Path(base) / "ConfereAntes"
    return Path.home() / ".confereantes"


class HistoryStore:
    def __init__(self, data_dir: Path | None = None) -> None:
        self.data_dir = data_dir or default_data_dir()
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.database_path = self.data_dir / "historico.sqlite3"
        self.key_path = self.data_dir / "historico.key"
        self._fernet = Fernet(self._load_or_create_key())
        self._initialize()

    def save(
        self,
        result: AnalysisResult,
        *,
        original_text: str = "",
        received_text: str = "",
    ) -> int:
        payload = {
            "score": result.score,
            "level": result.level,
            "summary": result.summary,
            "findings": [asdict(finding) for finding in result.findings],
            "original_excerpt": _excerpt(original_text),
            "received_excerpt": _excerpt(received_text),
        }
        encrypted = self._fernet.encrypt(json.dumps(payload, ensure_ascii=False).encode("utf-8"))
        created_at = datetime.now(UTC).isoformat()
        with sqlite3.connect(self.database_path) as connection:
            cursor = connection.execute(
                "INSERT INTO analyses (created_at, payload) VALUES (?, ?)",
                (created_at, encrypted),
            )
            return int(cursor.lastrowid)

    def list(self, *, limit: int = 30) -> list[HistoryEntry]:
        entries: list[HistoryEntry] = []
        with sqlite3.connect(self.database_path) as connection:
            rows = connection.execute(
                "SELECT id, created_at, payload FROM analyses ORDER BY id DESC LIMIT ?",
                (max(1, min(limit, 100)),),
            ).fetchall()
        for row_id, created_at, encrypted in rows:
            try:
                payload = json.loads(self._fernet.decrypt(encrypted).decode("utf-8"))
            except (InvalidToken, UnicodeDecodeError, json.JSONDecodeError):
                continue
            findings = [Finding(**item) for item in payload.get("findings", [])]
            entries.append(
                HistoryEntry(
                    id=int(row_id),
                    created_at=datetime.fromisoformat(created_at),
                    level=payload["level"],
                    score=int(payload["score"]),
                    summary=payload["summary"],
                    findings=findings,
                    original_excerpt=payload.get("original_excerpt", ""),
                    received_excerpt=payload.get("received_excerpt", ""),
                )
            )
        return entries

    def clear(self) -> None:
        with sqlite3.connect(self.database_path) as connection:
            connection.execute("DELETE FROM analyses")

    def _load_or_create_key(self) -> bytes:
        if self.key_path.exists():
            return self.key_path.read_bytes().strip()
        key = Fernet.generate_key()
        try:
            with self.key_path.open("xb") as handle:
                handle.write(key)
        except FileExistsError:
            return self.key_path.read_bytes().strip()
        return key

    def _initialize(self) -> None:
        with sqlite3.connect(self.database_path) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS analyses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    payload BLOB NOT NULL
                )
                """
            )


def _excerpt(text: str, *, limit: int = 180) -> str:
    compact = " ".join(text.split())
    return compact if len(compact) <= limit else f"{compact[: limit - 1]}…"
