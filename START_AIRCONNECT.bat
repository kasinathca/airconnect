@echo off
setlocal
cd /d "%~dp0"
if not exist "site\index.html" (
  echo ERROR: site\index.html was not found. Extract the entire ZIP first.
  pause
  exit /b 1
)
start "" "%~dp0site\index.html"
endlocal
