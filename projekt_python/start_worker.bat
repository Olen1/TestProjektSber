@echo off
echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo Starting Dramatiq worker...
python -m dramatiq knowledge_platform --processes 1 --threads 4

