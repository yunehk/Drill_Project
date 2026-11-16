@echo off
chcp 65001 >nul
cd /d "%~dp0"
python main.py
if errorlevel 1 (
  echo.
  echo 실행에 실패했습니다. Python 설치 후 다음 명령을 실행하세요:
  echo python -m pip install -r requirements.txt
  pause
)
