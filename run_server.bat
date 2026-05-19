@echo off
setlocal

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    py -3 -m venv .venv
)

call ".venv\Scripts\activate.bat"
python -m pip install -r requirements.txt

set "POMODORO_HUB_HOST=0.0.0.0"
set "POMODORO_HUB_PORT=8000"

echo.
echo PomodoroHub Server
echo ------------------
echo Server listening on port %POMODORO_HUB_PORT%.
echo Use this computer's LAN IP in the desktop app, for example:
echo http://192.168.0.10:%POMODORO_HUB_PORT%
echo.
echo If other PCs cannot connect, allow this app/port in Windows Firewall.
echo.

python main.py
pause
