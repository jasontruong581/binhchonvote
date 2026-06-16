from __future__ import annotations

from logging import Logger

from .models import AccountRecord
from .sites.base import SiteFlowContext
from .sites.dantri.flow import DanTriFlow


def run_single_account_flow(
    *,
    url: str,
    account: AccountRecord,
    headless: bool,
    timeout_ms: int,
    logger: Logger,
) -> None:
    DanTriFlow().run(
        url=url,
        context=SiteFlowContext(
            account=account,
            headless=headless,
            timeout_ms=timeout_ms,
            logger=logger,
        ),
    )
