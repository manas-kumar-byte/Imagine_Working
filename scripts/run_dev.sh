#!/usr/bin/env bash
# Spins up backend and frontend together for local dev.
set -e
(cd backend && uvicorn api.main:app --reload --port 8000) &
BACKEND_PID=$!
(cd frontend && npm run dev) &
FRONTEND_PID=$!
trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
wait
