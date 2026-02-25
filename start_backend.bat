@echo off
cd src\fastapi
python -m uvicorn app.main:app --host 127.0.0.1 --port 8080
