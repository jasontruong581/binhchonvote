# DanTri Vote Batch Tester Plan

## Goal

Build a Windows-friendly Python CLI tool that runs a batch flow on staging:

1. Open a target DanTri contest URL
2. Register a new account from CSV data
3. Log in with the created account
4. Navigate to `Bình chọn tác phẩm`
5. Click the vote reaction
6. Log out
7. Repeat for a requested batch size

Output must support source execution and packaged `.exe` execution on Windows 11.

## Fixed Decisions

- Language: Python
- Browser automation: Playwright for Python
- Interface: CLI
- Packaging: PyInstaller
- Password: hardcoded `123123`
- Batch mode: sequential
- Headless: CLI param
- CSV input: `--csv <path>` or fallback to CSV files next to `.exe`
- Used-state: persist only after full success
- Runtime state path: `%LOCALAPPDATA%\DanTriVoteTester`
- Frontend cannot be changed, so selectors must rely on visible text, labels, and DOM structure

## Success Criteria

- App can load CSV rows encoded in UTF-8
- App skips previously successful emails across runs
- Single-account failure does not crash the whole batch
- Logs and screenshots are written to runtime state dir
- App works in headed and headless mode
- Packaged `.exe` runs on Windows 11

## Architecture

```text
app/
  __init__.py
  main.py
  cli.py
  config.py
  models.py
  csv_pool.py
  state_store.py
  logger.py
  browser_flow.py
  selectors.py
  errors.py
```

## Phase 1

Scaffold the project and runtime path handling.

Deliverables:

- Python package structure under `app/`
- Config module for defaults and paths
- Runtime directory creation under `%LOCALAPPDATA%\DanTriVoteTester`
- Basic models and error types

## Phase 2

Implement CSV pool and used-state persistence.

Deliverables:

- CSV loading with `utf-8-sig`
- Support one explicit CSV path or fallback CSV discovery near executable
- `used_emails.txt`
- `run_results.csv`
- Selection of random unused accounts

## Phase 3

Implement CLI and batch orchestration.

Deliverables:

- `argparse` CLI
- Required args: `--url`, `--count`
- Optional args: `--csv`, `--headless`, `--delay-ms`, `--timeout-ms`, `--state-dir`
- Summary output and failure-safe batching

## Phase 4

Implement Playwright browser flow for one account.

Deliverables:

- Open page
- Click `Đăng nhập`
- Switch to `Đăng ký`
- Fill register form
- Wait for success or switch back to login tab
- Login with created account
- Locate `Bình chọn tác phẩm`
- Click vote reaction
- Logout

## Phase 5

Harden automation and package it.

Deliverables:

- Retry logic for transient UI failures
- Screenshots on error
- Structured logging
- `build.ps1`
- PyInstaller build flow
- README usage notes

## Risks

- UI selectors may change because there is no `data-testid`
- Contest pages may render slightly differently across entries
- Reaction controls may need contextual locating instead of direct selectors
- Packaged Playwright runtime may need explicit browser install guidance

## Implementation Notes

- Do not use hashed CSS classes as primary selectors
- Prefer visible text, labels, and scoped locators
- Mark email as used only after `register -> login -> vote -> logout` succeeds
- Keep batch execution sequential until selectors are proven stable

## Current Status

- Phase 1: completed
- Phase 2: completed
- Phase 3: completed
- Phase 4: in progress
- Phase 5: pending
