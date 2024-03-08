@echo off

:: Step 1: Download and Install Python
echo Installing Python...
choco install python --yes

:: Step 2: Create Virtual Environment
echo Creating Virtual Environment...
python -m venv snoc_env

:: Step 3: Activate Virtual Environment
echo Activating Virtual Environment...
call snoc_env\Scripts\activate

:: Step 4: Install Required Libraries
echo Installing Required Libraries...
pip install -r requirements.txt

echo Setup complete.
