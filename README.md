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

## Run From Source

Interactive mode:

```powershell
python -m app.main
```

The app will ask for:

1. CSV file path
2. target URL
3. run count

Flag-based mode:

```powershell
python -m app.main --url "YOUR_TARGET_URL" --count 10 --csv "D:\path\to\emails.csv" --state-dir "D:\path\to\.runtime" --headless true --timeout-ms 90000 --delay-ms 300
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

## Parameters

- `--url`: target contest entry URL
- `--count`: number of accounts to process
- `--csv`: input CSV file path
- `--state-dir`: where logs and run state are stored
- `--headless true|false`: browser visibility, default is `true`
- `--timeout-ms`: step timeout in milliseconds
- `--timeout-ms`: total time budget per account in milliseconds
- `--delay-ms`: delay between accounts in milliseconds

## Output Files

Each run writes to the selected `--state-dir`:

- `run_results.csv`
- `run.log`
- `screenshots\`

## Notes

- The app updates the input CSV directly.
- If the `used` column does not exist, the app adds it automatically.
- Only rows with empty `used` are eligible for selection.
- Every attempted account is marked `used=1`, including failed attempts.
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

The packaged build can run directly because `build.ps1` copies Playwright browsers into the output folder:

```powershell
.\dist\vote-batch\vote-batch.exe --url "YOUR_TARGET_URL" --count 10 --csv "D:\Hoang Code AI\Side Project\binhchondantri\vietnamese_names_10000_with_emailUTF8.csv" --state-dir "D:\Hoang Code AI\Side Project\binhchondantri\.runtime-exe-test" --headless true --timeout-ms 90000 --delay-ms 300
```

Smoke test example:

```powershell
.\dist\vote-batch\vote-batch.exe --url "YOUR_TARGET_URL" --count 1 --csv "D:\Hoang Code AI\Side Project\binhchondantri\vietnamese_names_10000_with_emailUTF8.csv" --state-dir "D:\Hoang Code AI\Side Project\binhchondantri\.runtime-exe-smoke" --headless true --timeout-ms 90000 --delay-ms 0
```

Notes:

- If you want prompt-based input instead of flags, just run `.\dist\vote-batch\vote-batch.exe` and answer the questions in the console.
- If you do not pass `--headless`, the app runs with browser hidden by default.
- Runtime state still goes to the chosen `--state-dir`.

## Run On Another Machine

If you pull this repo to another Windows machine, use this flow:

1. Install Python 3.10 or newer.
2. Open PowerShell in the project folder.
3. Install dependencies:

```powershell
python -m pip install -r requirements.txt
python -m playwright install chromium
```

4. Run from source:

```powershell
python -m app.main
```

If you want to create a fresh `.exe` on that machine:

```powershell
python -m pip install pyinstaller
powershell -ExecutionPolicy Bypass -File .\build.ps1
```

Then run:

```powershell
.\dist\vote-batch\vote-batch.exe
```

Important:

- Bring your own CSV file to that machine.
- The app updates the CSV directly by writing `used=1`.
- Do not run the `.exe` from inside the `build` folder. Use the file in `dist\vote-batch\vote-batch.exe`.
- If Windows blocks the app, right-click the file, open `Properties`, then allow/unblock it if needed.
