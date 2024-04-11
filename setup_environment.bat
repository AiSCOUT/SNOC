@echo off

:: Step 1: Download and Install Chocolatey (if not already installed)
echo Installing Chocolatey...
@"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -InputFormat None -ExecutionPolicy Bypass -Command "iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))" && SET "PATH=%PATH%;%ALLUSERSPROFILE%\chocolatey\bin"

:: Step 2: Download and Install Python
echo Installing Python...
choco install python --yes

:: Step 3: Create Virtual Environment
echo Creating Virtual Environment...
python -m venv snoc_env

:: Step 4: Activate Virtual Environment
echo Activating Virtual Environment...
call snoc_env\Scripts\activate

:: Step 5: Install Required Libraries
echo Installing Required Libraries...
pip install -r requirements.txt

echo Install Drill Automation Utilties
pip install git+https://github.com/AiSCOUT/Automation-DrillUtils.git@AT-357

echo Setup complete.
