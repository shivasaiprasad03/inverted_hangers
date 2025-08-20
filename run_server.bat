@echo off
cd /d %~dp0
cd ../my_learning_path/backend
C:/python_files/inverted_hangers/.venv/Scripts/python.exe -m uvicorn app:app --reload --host 127.0.0.1 --port 8000
