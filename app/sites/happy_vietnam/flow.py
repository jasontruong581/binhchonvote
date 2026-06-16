from __future__ import annotations

from ...errors import BrowserStepError
from ..base import SiteFlowContext
from ..helpers import wait_for_manual_checkpoint
from .selectors import DEFAULT_PASSWORD, LOGIN_URL, SIGNUP_URL


class HappyVietnamFlow:
    site_key = "happy_vietnam"

    def run(self, *, url: str, context: SiteFlowContext) -> None:
        if context.headless:
            raise BrowserStepError(
                status="LOGIN_FAILED",
                step="startup",
                message="Happy Vietnam flow requires --headless false because CAPTCHA must be completed manually.",
            )

        context.logger.info(
            "Happy Vietnam adapter initialized for url=%s using manual CAPTCHA checkpoints and default password length=%s",
            url,
            len(DEFAULT_PASSWORD),
        )

        wait_for_manual_checkpoint(
            context=context,
            instruction=(
                f"Mo browser va dang ky tai {SIGNUP_URL} cho email {context.account.email} "
                f"voi mat khau mac dinh {DEFAULT_PASSWORD}. "
                "Hoan tat CAPTCHA va submit dang ky bang tay."
            ),
        )
        wait_for_manual_checkpoint(
            context=context,
            instruction=(
                f"Tiep tuc dang nhap tai {LOGIN_URL} cho email {context.account.email}, "
                "hoan tat CAPTCHA bang tay, sau do mo trang vote va xac nhan account da san sang."
            ),
        )

        raise BrowserStepError(
            status="UNEXPECTED_ERROR",
            step="happy_vietnam_not_implemented",
            message=(
                "Happy Vietnam adapter scaffolded successfully. "
                "Please implement the post-login vote/logout steps in app/sites/happy_vietnam/flow.py."
            ),
        )
