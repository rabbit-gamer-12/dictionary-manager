# Dictionary Manager App

A runnable Python app for managing:
- general dictionary entries
- book links and page references
- Windows shortcut notes
- language translations
- a password-protected encrypted vault for private notes

## Quick start (run as an app)

### Windows (easiest)
1. Install Python 3.10+ from https://www.python.org/downloads/
2. In this folder, double-click **`run_app.bat`**

That script installs dependencies and launches the app menu.

### macOS / Linux
From this repo folder:

```bash
./run_app.sh
```

### Manual run (all platforms)

```bash
python -m pip install -r requirements.txt
python "high school manager/high_school_manager.py"
```

## First run behavior
- You will be prompted to create a **master password**.
- App data is stored in JSON files under `high school manager/`.
- Vault secrets are encrypted using:
  - `high school manager/secret.key`
  - `high school manager/codes_passwords.enc`

## Optional: make a desktop executable (.exe)
If you want a one-click executable with no terminal setup:

```bash
python -m pip install pyinstaller
pyinstaller --onefile --name DictionaryManager "high school manager/high_school_manager.py"
```

Then run `dist/DictionaryManager.exe`.
