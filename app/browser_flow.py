from __future__ import annotations

import time
from logging import Logger

from .config import DEFAULT_PASSWORD
from .errors import BrowserStepError
from .models import AccountRecord
from .selectors import (
    AUTH_TAB_SELECTOR,
    HEADER_ACCOUNT_BUTTON_SELECTOR,
    LOGIN_EMAIL_INPUT_SELECTOR,
    LOGIN_PASSWORD_INPUT_SELECTOR,
    LOGIN_SUBMIT_SELECTOR,
    LOGOUT_TEXT_CANDIDATES,
    NAVIGATION_BUTTON_SELECTOR,
    REACTION_CONTAINER_SELECTOR,
    REGISTER_NAME_INPUT_SELECTOR,
    REGISTER_SUBMIT_SELECTOR,
    USER_MENU_BUTTON_SELECTOR,
    VOTE_SECTION_TEXT,
)


def _raise_step(status: str, step: str, message: str) -> None:
    raise BrowserStepError(status=status, step=step, message=message)


def _type_text(locator, value: str) -> None:
    locator.click()
    locator.press("Control+A")
    locator.type(value, delay=20)


def _wait_for_submit_enabled(locator, timeout_ms: int) -> None:
    locator.wait_for(state="visible", timeout=timeout_ms)
    locator.evaluate(
        """(el, timeoutMs) => new Promise((resolve, reject) => {
            const start = Date.now();
            const check = () => {
                const disabled = el.hasAttribute('disabled') || el.className.includes('dt-pointer-events-none');
                if (!disabled) {
                    resolve(true);
                    return;
                }
                if (Date.now() - start > timeoutMs) {
                    reject(new Error('Submit button remained disabled'));
                    return;
                }
                setTimeout(check, 100);
            };
            check();
        })""",
        timeout_ms,
    )


def _remaining_timeout(deadline: float) -> int:
    remaining_ms = int((deadline - time.monotonic()) * 1000)
    if remaining_ms <= 0:
        raise TimeoutError("Account time budget exhausted")
    return remaining_ms


def _first_visible(locator):
    count = locator.count()
    for index in range(count):
        candidate = locator.nth(index)
        if candidate.is_visible():
            return candidate
    return None


def _open_auth_modal(page, deadline: float) -> None:
    try:
        page.locator(NAVIGATION_BUTTON_SELECTOR).first.click(force=True, timeout=_remaining_timeout(deadline))
        page.wait_for_timeout(1000)
        account_button = page.locator(HEADER_ACCOUNT_BUTTON_SELECTOR).first
        account_button.wait_for(state="visible", timeout=_remaining_timeout(deadline))
        account_button.click(force=True, timeout=_remaining_timeout(deadline))
        page.wait_for_timeout(1200)
    except Exception as exc:
        _raise_step("LOGIN_FAILED", "open_auth_modal", str(exc))


def run_single_account_flow(
    *,
    url: str,
    account: AccountRecord,
    headless: bool,
    timeout_ms: int,
    logger: Logger,
) -> None:
    try:
        from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        _raise_step("UNEXPECTED_ERROR", "import_playwright", str(exc))

    with sync_playwright() as playwright:
        deadline = time.monotonic() + (timeout_ms / 1000)
        browser = playwright.chromium.launch(headless=headless)
        context = browser.new_context()
        page = context.new_page()
        page.set_default_timeout(min(timeout_ms, 30000))

        try:
            logger.info("Navigating to url=%s", url)
            page.goto(url, wait_until="domcontentloaded", timeout=_remaining_timeout(deadline))
            page.wait_for_timeout(5000)

            try:
                _open_auth_modal(page, deadline)
            except BrowserStepError:
                raise

            try:
                auth_tabs = page.locator(AUTH_TAB_SELECTOR)
                if auth_tabs.count() < 2:
                    _raise_step("REGISTER_FAILED", "open_register_tab", "Register tab not found")
                auth_tabs.nth(1).click(timeout=_remaining_timeout(deadline))
                page.wait_for_timeout(800)
            except BrowserStepError:
                raise
            except Exception as exc:
                _raise_step("REGISTER_FAILED", "open_register_tab", str(exc))

            try:
                register_name = _first_visible(page.locator(REGISTER_NAME_INPUT_SELECTOR))
                register_email = _first_visible(page.locator(LOGIN_EMAIL_INPUT_SELECTOR))
                register_password = _first_visible(page.locator(LOGIN_PASSWORD_INPUT_SELECTOR))
                if register_name is None or register_email is None or register_password is None:
                    _raise_step("REGISTER_FAILED", "fill_register_form", "Visible register inputs not found")
                _type_text(register_name, account.name)
                _type_text(register_email, account.email)
                _type_text(register_password, DEFAULT_PASSWORD)
                page.keyboard.press("Tab")
                page.wait_for_timeout(800)
            except Exception as exc:
                _raise_step("REGISTER_FAILED", "fill_register_form", str(exc))

            try:
                register_submit = page.locator(REGISTER_SUBMIT_SELECTOR)
                _wait_for_submit_enabled(register_submit, _remaining_timeout(deadline))
                register_submit.click(force=True, timeout=_remaining_timeout(deadline))
                page.wait_for_timeout(2500)
            except Exception as exc:
                _raise_step("REGISTER_FAILED", "submit_register", str(exc))

            try:
                auth_tabs = page.locator(AUTH_TAB_SELECTOR)
                auth_tabs.first.wait_for(timeout=_remaining_timeout(deadline))
                auth_tabs.first.click(timeout=_remaining_timeout(deadline))
                page.wait_for_timeout(500)
            except PlaywrightTimeoutError as exc:
                _raise_step("REGISTER_FAILED", "wait_register_success", str(exc))

            try:
                login_email = _first_visible(page.locator(LOGIN_EMAIL_INPUT_SELECTOR))
                login_password = _first_visible(page.locator(LOGIN_PASSWORD_INPUT_SELECTOR))
                if login_email is None or login_password is None:
                    _raise_step("LOGIN_FAILED", "fill_login_form", "Visible login inputs not found")
                _type_text(login_email, account.email)
                _type_text(login_password, DEFAULT_PASSWORD)
                page.keyboard.press("Tab")
                page.wait_for_timeout(1000)
            except Exception as exc:
                _raise_step("LOGIN_FAILED", "fill_login_form", str(exc))

            try:
                login_submit = page.locator(LOGIN_SUBMIT_SELECTOR)
                _wait_for_submit_enabled(login_submit, _remaining_timeout(deadline))
                login_submit.click(force=True, timeout=_remaining_timeout(deadline))
                page.wait_for_timeout(3000)
            except Exception as exc:
                _raise_step("LOGIN_FAILED", "submit_login", str(exc))

            try:
                page.wait_for_timeout(1500)
                overlay = page.locator(".auth-overlay")
                if overlay.count() > 0 and overlay.first.is_visible():
                    page.keyboard.press("Escape")
                    page.wait_for_timeout(800)
                nav_button = page.locator(NAVIGATION_BUTTON_SELECTOR).first
                nav_button.click(force=True, timeout=_remaining_timeout(deadline))
                page.wait_for_timeout(1500)
            except Exception as exc:
                _raise_step("LOGIN_FAILED", "close_navigation_after_login", str(exc))

            try:
                vote_heading = page.get_by_text(VOTE_SECTION_TEXT, exact=False)
                vote_heading.first.wait_for(timeout=_remaining_timeout(deadline))
                vote_heading.first.scroll_into_view_if_needed()
                page.wait_for_timeout(1500)
            except PlaywrightTimeoutError as exc:
                _raise_step("VOTE_FAILED", "locate_vote_section", str(exc))

            try:
                reaction = page.locator(REACTION_CONTAINER_SELECTOR).first
                reaction.wait_for(timeout=_remaining_timeout(deadline))
                reaction.scroll_into_view_if_needed()
                page.wait_for_timeout(3000)
                reaction_buttons = reaction.locator("button")
                reaction_buttons.last.wait_for(timeout=_remaining_timeout(deadline))
                reaction_buttons.last.click(force=True, timeout=_remaining_timeout(deadline))
                page.wait_for_timeout(2000)
            except Exception as exc:
                _raise_step("VOTE_FAILED", "click_vote_button", str(exc))

            try:
                page.evaluate("window.scrollTo(0, 0)")
                page.wait_for_timeout(1200)
                user_menu = page.locator(USER_MENU_BUTTON_SELECTOR)
                if user_menu.count() == 0:
                    _raise_step("LOGOUT_FAILED", "open_user_menu", "User menu button not found")
                user_menu.first.click(force=True, timeout=_remaining_timeout(deadline))
                page.wait_for_timeout(1000)

                logout_clicked = False
                for candidate in LOGOUT_TEXT_CANDIDATES:
                    text_locator = page.get_by_text(candidate, exact=False)
                    if text_locator.count() > 0:
                        text_locator.first.click(force=True, timeout=_remaining_timeout(deadline))
                        logout_clicked = True
                        break

                if not logout_clicked:
                    href_locator = page.locator('a[href*="logout"], a[href*="dang-xuat"]')
                    if href_locator.count() > 0:
                        href_locator.first.click(force=True, timeout=_remaining_timeout(deadline))
                        logout_clicked = True

                if not logout_clicked:
                    _raise_step("LOGOUT_FAILED", "logout", "Logout control not found")
            except BrowserStepError:
                raise
            except TimeoutError as exc:
                _raise_step("UNEXPECTED_ERROR", "account_timeout", str(exc))
            except Exception as exc:
                _raise_step("LOGOUT_FAILED", "logout", str(exc))
        except TimeoutError as exc:
            _raise_step("UNEXPECTED_ERROR", "account_timeout", str(exc))
        finally:
            context.close()
            browser.close()
