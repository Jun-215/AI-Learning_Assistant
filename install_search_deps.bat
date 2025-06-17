@echo off
echo Installing improved search dependencies...
cd /d "%~dp0backend"
pip install -r requirements.txt
echo.
echo Dependencies installed successfully!
echo.
echo You can now test the improved search functionality by running:
echo python ../test_search.py
echo.
pause
