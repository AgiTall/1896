@echo off
cd /d "%~dp0"
set "editor_runtime=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if exist "%editor_runtime%" (
 "%editor_runtime%" country_editor.py
 goto finished
)
where py >nul 2>nul
if not errorlevel 1 (
 py -3 country_editor.py
) else (
 python country_editor.py
)
:finished
if errorlevel 1 (
 echo Install Python 3 with tkinter and Pillow: pip install -r country_editor_requirements.txt
 pause
)
