@echo off

:: Step 1: Activate virtual environment
call venv\Scripts\activate

:: Step 2: Install PyInstaller without restart warning
pip install --upgrade pyinstaller

:: Step 3: Create the executable using PyInstaller
pyinstaller main.spec

echo Build complete. Find the executable in the dist folder.

:: Step 4: Deactivate virtual environment
deactivate
