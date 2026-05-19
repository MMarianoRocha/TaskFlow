@echo off
setlocal

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    py -3 -m venv .venv
)

call ".venv\Scripts\activate.bat"
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if exist "dist\PomodoroHubServer.exe" del "dist\PomodoroHubServer.exe"
if exist "dist\PomodoroHubClient.exe" del "dist\PomodoroHubClient.exe"

python -m PyInstaller --clean --onefile --name PomodoroHubServer --hidden-import passlib.handlers.bcrypt main.py
python -m PyInstaller --clean --onefile --windowed --name PomodoroHubClient desktop_app.py

echo.
echo Build finished.
echo Server EXE: dist\PomodoroHubServer.exe
echo Client EXE: dist\PomodoroHubClient.exe
echo.
pause
