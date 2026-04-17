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

        if not self.paths.results_file.exists():
            with self.paths.results_file.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.writer(handle)
                writer.writerow(RESULT_HEADERS)

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
