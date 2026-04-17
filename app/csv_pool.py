from __future__ import annotations

import csv
import random
import re
from pathlib import Path

from .errors import CsvDataError, CsvResolutionError, InsufficientAccountsError
from .models import AccountRecord


EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
USED_COLUMN = "used"
TRUTHY_USED_VALUES = {"1", "true", "yes", "y", "used", "success"}
NAME_KEYS = (
    "name",
    "full_name",
    "full name",
    "fullname",
    "ho va ten",
    "họ và tên",
)
EMAIL_KEYS = ("email", "mail")


def resolve_csv_path(explicit_csv_path: Path | None) -> Path:
    if explicit_csv_path is None:
        raise CsvResolutionError("A CSV file path is required.")

    path = explicit_csv_path.expanduser().resolve()
    if not path.exists() or not path.is_file():
        raise CsvResolutionError(f"CSV file not found: {path}")
    if path.suffix.lower() != ".csv":
        raise CsvResolutionError(f"Expected a .csv file but received: {path}")
    return path


def _extract_value(row: dict[str, str], keys: tuple[str, ...]) -> str:
    lowered = {str(key).strip().lower(): str(value or "") for key, value in row.items()}
    for key in keys:
        value = lowered.get(key)
        if value is not None and value.strip():
            return value.strip()
    return ""


def _is_used(value: str) -> bool:
    return value.strip().lower() in TRUTHY_USED_VALUES


class CsvAccountPool:
    def __init__(
        self,
        csv_path: Path,
        fieldnames: list[str],
        rows: list[dict[str, str]],
    ) -> None:
        self.csv_path = csv_path
        self.fieldnames = fieldnames
        self.rows = rows

    @classmethod
    def load(cls, csv_path: Path) -> "CsvAccountPool":
        with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if not reader.fieldnames:
                raise CsvDataError(f"CSV has no header row: {csv_path}")

            fieldnames = [str(name) for name in reader.fieldnames]
            rows = [{key: str(value or "") for key, value in row.items()} for row in reader]

        pool = cls(csv_path=csv_path, fieldnames=fieldnames, rows=rows)
        if USED_COLUMN not in pool.fieldnames:
            pool.fieldnames.append(USED_COLUMN)
            for row in pool.rows:
                row[USED_COLUMN] = ""
            pool.save()
        else:
            for row in pool.rows:
                row.setdefault(USED_COLUMN, "")

        if not pool.rows:
            raise CsvDataError(f"CSV contains no data rows: {csv_path}")
        return pool

    def save(self) -> None:
        with self.csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=self.fieldnames)
            writer.writeheader()
            writer.writerows(self.rows)

    def select_random_unused_accounts(self, count: int) -> list[AccountRecord]:
        available: list[AccountRecord] = []
        for row_index, row in enumerate(self.rows):
            name = _extract_value(row, NAME_KEYS)
            email = _extract_value(row, EMAIL_KEYS)
            if not name or not email:
                continue

            normalized_email = email.lower()
            if not EMAIL_PATTERN.match(normalized_email):
                continue
            if _is_used(row.get(USED_COLUMN, "")):
                continue

            available.append(
                AccountRecord(
                    name=name,
                    email=normalized_email,
                    source_csv=self.csv_path,
                    row_index=row_index,
                )
            )

        if len(available) < count:
            raise InsufficientAccountsError(
                f"Requested {count} accounts but only {len(available)} unused accounts remain."
            )
        return random.sample(available, count)

    def mark_used(self, account: AccountRecord) -> None:
        self.rows[account.row_index][USED_COLUMN] = "1"
        self.save()


def load_account_pool(csv_path: Path) -> CsvAccountPool:
    return CsvAccountPool.load(csv_path)
