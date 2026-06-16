from __future__ import annotations

from dataclasses import dataclass
from logging import Logger
from typing import Protocol

from ..models import AccountRecord


@dataclass(frozen=True)
class SiteFlowContext:
    account: AccountRecord
    headless: bool
    timeout_ms: int
    logger: Logger


class SiteFlow(Protocol):
    site_key: str

    def run(self, *, url: str, context: SiteFlowContext) -> None:
        """Run the site-specific browser flow for a single account."""
