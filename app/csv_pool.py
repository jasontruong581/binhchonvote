from __future__ import annotations

import csv
import re
import random
from pathlib import Path

from .config import get_app_base_dir
from .errors import CsvDataError, CsvResolutionError, InsufficientAccountsError
from .models import AccountRecord


SUPPORTED_SUFFIXES = {".csv"}
EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


def resolve_csv_candidates(explicit_csv_path: Path | None) -> list[Path]:
    if explicit_csv_path is not None:
        path = explicit_csv_path.expanduser().resolve()
        if not path.exists() or not path.is_file():
            raise CsvResolutionError(f"CSV file not found: {path}")
        return [path]

    base_dir = get_app_base_dir()
    candidates = sorted(
        path.resolve()
        for path in base_dir.iterdir()
        if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES
    )
    if not candidates:
        raise CsvResolutionError(
            f"No CSV files found in fallback directory: {base_dir}"
        )
    return candidates


def _extract_value(row: dict[str, str], keys: tuple[str, ...]) -> str:
    lowered = {str(key).strip().lower(): value for key, value in row.items()}
    for key in keys:
        value = lowered.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()
    return ""


def load_accounts_from_csv(path: Path) -> list[AccountRecord]:
    records: list[AccountRecord] = []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise CsvDataError(f"CSV has no header row: {path}")

        for row in reader:
            name = _extract_value(
                row,
                ("name", "full_name", "full name", "fullname", "ho va ten", "họ và tên"),
            )
            email = _extract_value(row, ("email", "mail"))
            if not name or not email:
                continue
            normalized_email = email.lower()
            if not EMAIL_PATTERN.match(normalized_email):
                continue
            records.append(AccountRecord(name=name, email=normalized_email, source_csv=path))

    if not records:
        raise CsvDataError(f"No usable name/email rows found in CSV: {path}")
    return records


def load_accounts(csv_candidates: list[Path]) -> list[AccountRecord]:
    records: list[AccountRecord] = []
    for candidate in csv_candidates:
        records.extend(load_accounts_from_csv(candidate))
    return records


def select_random_unused_accounts(
    accounts: list[AccountRecord],
    used_emails: set[str],
    count: int,
) -> list[AccountRecord]:
    available = [account for account in accounts if account.email.lower() not in used_emails]
    if len(available) < count:
        raise InsufficientAccountsError(
            f"Requested {count} accounts but only {len(available)} unused accounts remain."
        )
    return random.sample(available, count)
