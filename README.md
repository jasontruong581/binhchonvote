#  Vote Batch Tester

Python CLI tool for staged batch testing of:

1. register
2. login
3. vote
4. logout

## Requirements

- Windows 11
- Python 3.10+
- Internet access

## Setup

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Install Playwright Chromium:

```powershell
python -m playwright install chromium
```

## Standard Commands

Run a single visible smoke test:

```powershell
python -m app.main --url "YOUR_TARGET_URL" --count 1 --csv "D:\Hoang Code AI\Side Project\binhchondantri\vietnamese_names_10000_with_emailUTF8.csv" --state-dir "D:\Hoang Code AI\Side Project\binhchondantri\.runtime-smoke" --headless false --timeout-ms 25000 --delay-ms 0
```

Run batch 10 in headed mode:

```powershell
python -m app.main --url "YOUR_TARGET_URL" --count 10 --csv "D:\Hoang Code AI\Side Project\binhchondantri\vietnamese_names_10000_with_emailUTF8.csv" --state-dir "D:\Hoang Code AI\Side Project\binhchondantri\.runtime-batch-10" --headless false --timeout-ms 90000 --delay-ms 1000
```

Run batch 50 in headless mode:

```powershell
python -m app.main --url "YOUR_TARGET_URL" --count 50 --csv "D:\Hoang Code AI\Side Project\binhchondantri\vietnamese_names_10000_with_emailUTF8.csv" --state-dir "D:\Hoang Code AI\Side Project\binhchondantri\.runtime-batch-50" --headless true --timeout-ms 90000 --delay-ms 300
```

Run by auto-discovering CSV files in the same folder as the app:

```powershell
python -m app.main --url "YOUR_TARGET_URL" --count 10 --state-dir "D:\Hoang Code AI\Side Project\binhchondantri\.runtime-auto-csv" --headless false --timeout-ms 90000 --delay-ms 1000
```

## Parameters

- `--url`: target contest entry URL
- `--count`: number of accounts to process
- `--csv`: optional explicit CSV file path
- `--state-dir`: where logs and run state are stored
- `--headless true|false`: browser visibility
- `--timeout-ms`: step timeout in milliseconds
- `--timeout-ms`: total time budget per account in milliseconds
- `--delay-ms`: delay between accounts in milliseconds

## Output Files

Each run writes to the selected `--state-dir`:

- `used_emails.txt`
- `run_results.csv`
- `run.log`
- `screenshots\`

## Notes

- Emails are marked as used only after a full successful flow.
- CSV rows with invalid email format are skipped.
- Each account now fails fast when its total budget is exhausted and the batch immediately moves to the next email.
- UI automation is selector-sensitive. If the website layout changes, update selectors in `app/selectors.py` and `app/browser_flow.py`.

## Build

Build the Windows executable:

```powershell
.\build.ps1
```

Executable output:

- `dist\vote-batch\vote-batch.exe`

## Run The Exe

If the packaged app is running on the same machine where Playwright browsers are already installed, set `PLAYWRIGHT_BROWSERS_PATH` before launching the `.exe`:

```powershell
$env:PLAYWRIGHT_BROWSERS_PATH="C:\Users\<your-user>\AppData\Local\ms-playwright"
.\dist\vote-batch\vote-batch.exe --url "YOUR_TARGET_URL" --count 10 --csv "D:\Hoang Code AI\Side Project\binhchondantri\vietnamese_names_10000_with_emailUTF8.csv" --state-dir "D:\Hoang Code AI\Side Project\binhchondantri\.runtime-exe-test" --headless true --timeout-ms 90000 --delay-ms 300
```

Smoke test example:

```powershell
$env:PLAYWRIGHT_BROWSERS_PATH="C:\Users\<your-user>\AppData\Local\ms-playwright"
.\dist\vote-batch\vote-batch.exe --url "YOUR_TARGET_URL" --count 1 --csv "D:\Hoang Code AI\Side Project\binhchondantri\vietnamese_names_10000_with_emailUTF8.csv" --state-dir "D:\Hoang Code AI\Side Project\binhchondantri\.runtime-exe-smoke" --headless true --timeout-ms 90000 --delay-ms 0
```

Notes:

- Without `PLAYWRIGHT_BROWSERS_PATH`, the current packaged build may not find Chromium automatically.
- Runtime state still goes to the chosen `--state-dir`.
