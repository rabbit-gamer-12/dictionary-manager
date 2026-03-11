@echo off
setlocal

cd /d "%~dp0"
python -m pip install -r requirements.txt
python "high school manager\high_school_manager.py"

endlocal
