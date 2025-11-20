@echo off
REM Setup script for Ownership Data Quality Assessment POC (Windows)
REM This script automates the installation and initial setup

echo ==========================================
echo Ownership DQ POC - Setup Script (Windows)
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found. Please install Python 3.9+ from python.org
    pause
    exit /b 1
)

echo Checking Python version...
python --version
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created
) else (
    echo Virtual environment already exists
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo Virtual environment activated
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip >nul 2>&1
echo Pip upgraded
echo.

REM Install requirements
echo Installing dependencies...
pip install -r requirements.txt
echo Dependencies installed
echo.

REM Download spaCy model
echo Downloading spaCy model for NLP...
python -m spacy download en_core_web_sm
echo spaCy model downloaded
echo.

REM Create necessary directories
echo Creating project directories...
if not exist "data" mkdir data
if not exist "reports" mkdir reports
if not exist "visualizations" mkdir visualizations
echo Directories created
echo.

echo ==========================================
echo Setup Complete!
echo ==========================================
echo.
echo To get started:
echo   1. Activate virtual environment: venv\Scripts\activate.bat
echo   2. Run the pipeline: python -m ownership_dq.main
echo   3. Launch dashboard: streamlit run ownership_dq\dashboard.py
echo.
echo For more information, see README.md
echo.
pause
