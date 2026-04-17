from __future__ import annotations

import argparse
from pathlib import Path

from .config import DEFAULT_DELAY_MS, DEFAULT_TIMEOUT_MS
from .models import CliOptions


def _parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "y", "on"}:
        return True
    if normalized in {"0", "false", "no", "n", "off"}:
        return False
    raise argparse.ArgumentTypeError(f"Invalid boolean value: {value}")


def parse_args() -> CliOptions:
    parser = argparse.ArgumentParser(description="DanTri batch vote flow tester")
    parser.add_argument("--url", help="Target contest entry URL")
    parser.add_argument("--count", type=int, help="Number of accounts to process")
    parser.add_argument("--csv", dest="csv_path", type=Path, help="Explicit CSV file path")
    parser.add_argument(
        "--headless",
        type=_parse_bool,
        default=True,
        help="Run browser in headless mode: true or false (default: true)",
    )
    parser.add_argument("--delay-ms", type=int, default=DEFAULT_DELAY_MS)
    parser.add_argument("--timeout-ms", type=int, default=DEFAULT_TIMEOUT_MS)
    parser.add_argument("--state-dir", type=Path, help="Override runtime state directory")
    parser.add_argument(
        "--screenshot-on-error",
        type=_parse_bool,
        default=True,
        help="Capture screenshots on failure: true or false",
    )

    args = parser.parse_args()
    csv_path = args.csv_path
    url = args.url
    count = args.count

    if csv_path is None:
        raw_csv = input("Nhap duong dan file CSV email: ").strip()
        if raw_csv:
            csv_path = Path(raw_csv)

    if not url:
        url = input("Nhap link URL web: ").strip()

    if count is None:
        while True:
            raw_count = input("Nhap so lan chay: ").strip()
            try:
                count = int(raw_count)
            except ValueError:
                print("So lan chay phai la so nguyen.")
                continue
            if count <= 0:
                print("So lan chay phai lon hon 0.")
                continue
            break

    return CliOptions(
        url=url,
        count=count,
        csv_path=csv_path,
        headless=args.headless,
        delay_ms=args.delay_ms,
        timeout_ms=args.timeout_ms,
        state_dir=args.state_dir,
        screenshot_on_error=args.screenshot_on_error,
    )
