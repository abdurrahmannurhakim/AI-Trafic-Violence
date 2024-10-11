@echo off

:: Step 1: Activate virtual environment
call venv\Scripts\activate

:: Step 2: Run
python reset.py

:: Step 3:  Deactivate virtual environment
echo Pricess complete.
deactivate
