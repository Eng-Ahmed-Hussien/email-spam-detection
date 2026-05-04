@echo off
echo Building SpamDetector.exe ...
pyinstaller --onefile --windowed --name SpamDetector --add-data "models;models" --add-data "src;src" app.py
echo Done. Check dist/SpamDetector.exe
pause
