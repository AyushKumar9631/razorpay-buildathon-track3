@echo off
echo ========================================
echo  Generating Test Data for Demo
echo ========================================
echo.

cd /d "%~dp0..\backend"

echo Setting up Python path...
set PYTHONPATH=%CD%

echo.
echo Running generate_test_data.py...
python ..\scripts\generate_test_data.py

echo.
echo ========================================
echo  Test Data Generation Complete!
echo ========================================
pause
