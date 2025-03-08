@echo off

REM Install dependencies using Poetry
echo Installing dependencies...
poetry install

REM Start the application using Waitress (for Flask)
echo Starting the server on port 5000...
poetry run waitress-serve --host=127.0.0.1 --port=5000 app:app

REM Alternatively, use Uvicorn for FastAPI or ASGI apps
REM poetry run uvicorn app:app --host 127.0.0.1 --port 5000 --reload

REM Keep the window open
pause