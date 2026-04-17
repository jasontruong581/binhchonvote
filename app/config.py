from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path


APP_NAME = "DanTriVoteTester"
DEFAULT_PASSWORD = "123123"
DEFAULT_DELAY_MS = 1000
DEFAULT_TIMEOUT_MS = 90000


def get_runtime_root(override: Path | None = None) -> Path:
    if override is not None:
        return override.expanduser().resolve()

    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        return Path(local_app_data).resolve() / APP_NAME

    return Path.home().resolve() / "AppData" / "Local" / APP_NAME


def get_app_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def configure_runtime_environment() -> None:
    if os.environ.get("PLAYWRIGHT_BROWSERS_PATH"):
        return

    if getattr(sys, "frozen", False):
        bundled_browsers = Path(sys.executable).resolve().parent / "ms-playwright"
        if bundled_browsers.exists():
            os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(bundled_browsers)


@dataclass(frozen=True)
class RuntimePaths:
    root: Path
    results_file: Path
    log_file: Path
    screenshots_dir: Path


def build_runtime_paths(override: Path | None = None) -> RuntimePaths:
    root = get_runtime_root(override)
    return RuntimePaths(
        root=root,
        results_file=root / "run_results.csv",
        log_file=root / "run.log",
        screenshots_dir=root / "screenshots",
    )
