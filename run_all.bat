@echo off
REM Runs Steps 5-9 automatically. Ollama must be running. Takes ~30-60 minutes. Keep laptop plugged in.
echo === Test run 1 (before fixes) ===
python tests\run_tests.py
echo === Analyzing weak outputs + applying prompt fixes ===
python tests\analyze.py
echo === Test run 2 (after fixes) ===
python tests\run_tests.py
echo === Building PDF report ===
python report\make_report.py
echo.
echo ALL DONE. Open report\final_report.pdf
pause
