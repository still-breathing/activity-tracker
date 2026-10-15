# Personal Activity tracker

Single-user PWA that shows my cycling activities from Strava.

## Stack

- Backend: Python, FastAPI, SQLite
- Frontend: vanilla JS, Leaflet, Chart.js, installable PWA
- Tests: pytest, run before declaring any task done

## Rules

- Secrets live in .env only. Never print, log, or commit them.
- Develop against fixtures in tests/fixtures/, not the live API.
- Write tests first. One small change at a time.
- Show a plan before editing multiple files.
- Most of the rides are commutes, so moving time matters, average speed both matters.
