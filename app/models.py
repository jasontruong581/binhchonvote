from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True)
class AccountRecord:
    name: str
    email: str
    source_csv: Path
    row_index: int


@dataclass(frozen=True)
class RunResult:
    timestamp: datetime
    url: str
    name: str
    email: str
    status: str
    step_failed: str
    message: str


@dataclass(frozen=True)
class CliOptions:
    url: str
    count: int
    csv_path: Path | None
    headless: bool
    delay_ms: int
    timeout_ms: int
    state_dir: Path | None
    screenshot_on_error: bool


class RunStatus:
    SUCCESS = "SUCCESS"
    REGISTER_FAILED = "REGISTER_FAILED"
    LOGIN_FAILED = "LOGIN_FAILED"
    VOTE_FAILED = "VOTE_FAILED"
    LOGOUT_FAILED = "LOGOUT_FAILED"
    UNEXPECTED_ERROR = "UNEXPECTED_ERROR"
