from __future__ import annotations

import csv
from pathlib import Path

from .config import RuntimePaths
from .models import RunResult


RESULT_HEADERS = [
    "timestamp",
    "url",
    "name",
    "email",
    "status",
    "step_failed",
    "message",
]


class StateStore:
    def __init__(self, paths: RuntimePaths) -> None:
        self.paths = paths

    def ensure_layout(self) -> None:
        self.paths.root.mkdir(parents=True, exist_ok=True)
        self.paths.screenshots_dir.mkdir(parents=True, exist_ok=True)
        self.paths.used_emails_file.touch(exist_ok=True)

        if not self.paths.results_file.exists():
            with self.paths.results_file.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.writer(handle)
                writer.writerow(RESULT_HEADERS)

    def load_used_emails(self) -> set[str]:
        if not self.paths.used_emails_file.exists():
            return set()

        emails: set[str] = set()
        with self.paths.used_emails_file.open("r", encoding="utf-8-sig") as handle:
            for line in handle:
                normalized = line.strip().lower()
                if normalized:
                    emails.add(normalized)
        return emails

    def append_used_email(self, email: str) -> None:
        normalized = email.strip().lower()
        if not normalized:
            return
        with self.paths.used_emails_file.open("a", encoding="utf-8-sig") as handle:
            handle.write(f"{normalized}\n")

    def append_result(self, result: RunResult) -> None:
        with self.paths.results_file.open("a", encoding="utf-8-sig", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(
                [
                    result.timestamp.isoformat(),
                    result.url,
                    result.name,
                    result.email,
                    result.status,
                    result.step_failed,
                    result.message,
                ]
            )
