from __future__ import annotations

import sys
import time
from datetime import datetime

from .browser_flow import run_single_account_flow
from .cli import parse_args
from .config import build_runtime_paths, configure_runtime_environment
from .csv_pool import load_account_pool, resolve_csv_path
from .errors import AppError, BrowserStepError
from .logger import configure_logging
from .models import RunResult, RunStatus
from .state_store import StateStore


def main() -> int:
    configure_runtime_environment()
    options = parse_args()
    runtime_paths = build_runtime_paths(options.state_dir)
    state_store = StateStore(runtime_paths)
    state_store.ensure_layout()
    logger = configure_logging(runtime_paths.log_file)

    try:
        csv_path = resolve_csv_path(options.csv_path)
        account_pool = load_account_pool(csv_path)
        selected_accounts = account_pool.select_random_unused_accounts(options.count)
    except AppError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    logger.info(
        "Starting batch run count=%s headless=%s csv_file=%s state_dir=%s",
        options.count,
        options.headless,
        csv_path,
        runtime_paths.root,
    )

    success_count = 0
    failure_count = 0

    for index, account in enumerate(selected_accounts, start=1):
        logger.info("Processing account %s/%s email=%s", index, options.count, account.email)
        try:
            run_single_account_flow(
                url=options.url,
                account=account,
                headless=options.headless,
                timeout_ms=options.timeout_ms,
                logger=logger,
            )
        except BrowserStepError as exc:
            failure_count += 1
            state_store.append_result(
                RunResult(
                    timestamp=datetime.now(),
                    url=options.url,
                    name=account.name,
                    email=account.email,
                    status=exc.status,
                    step_failed=exc.step,
                    message=str(exc),
                )
            )
            account_pool.mark_used(account)
            logger.error(
                "Account failed email=%s status=%s step=%s error=%s",
                account.email,
                exc.status,
                exc.step,
                exc,
            )
        except AppError as exc:
            failure_count += 1
            state_store.append_result(
                RunResult(
                    timestamp=datetime.now(),
                    url=options.url,
                    name=account.name,
                    email=account.email,
                    status=RunStatus.UNEXPECTED_ERROR,
                    step_failed="browser_flow",
                    message=str(exc),
                )
            )
            account_pool.mark_used(account)
            logger.error("Account failed email=%s error=%s", account.email, exc)
        except Exception as exc:
            failure_count += 1
            state_store.append_result(
                RunResult(
                    timestamp=datetime.now(),
                    url=options.url,
                    name=account.name,
                    email=account.email,
                    status=RunStatus.UNEXPECTED_ERROR,
                    step_failed="unhandled_exception",
                    message=str(exc),
                )
            )
            account_pool.mark_used(account)
            logger.exception("Unhandled failure email=%s", account.email)
        else:
            success_count += 1
            account_pool.mark_used(account)
            state_store.append_result(
                RunResult(
                    timestamp=datetime.now(),
                    url=options.url,
                    name=account.name,
                    email=account.email,
                    status=RunStatus.SUCCESS,
                    step_failed="",
                    message="Completed successfully",
                )
            )
            logger.info("Account completed email=%s", account.email)

        if index < len(selected_accounts) and options.delay_ms > 0:
            time.sleep(options.delay_ms / 1000)

    logger.info(
        "Batch finished requested=%s success=%s failure=%s results=%s",
        options.count,
        success_count,
        failure_count,
        runtime_paths.results_file,
    )
    return 0 if failure_count == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
