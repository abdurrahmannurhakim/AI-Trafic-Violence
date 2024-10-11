@echo off

:: Step 1: Activate virtual environment
call venv\Scripts\activate

:: Step 2: Install Python packages in virtual environment
pip install -r recruirments.txt

:: Step 3: Install VC_redist.x64.exe
echo Installing Visual C++ Redistributable...
VC_redist.x64.exe /quiet /norestart

echo Installation complete.

:: Step 4: Deactivate virtual environment
deactivate
