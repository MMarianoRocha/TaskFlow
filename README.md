# PomodoroHub

## Overview

PomodoroHub is a FastAPI backend for managing Pomodoro sessions across multiple users.
The desktop client is built with PySide6 and queries the backend to display a live overlay
showing who is currently in an active Pomodoro session.

The project is designed to run the backend on one dedicated machine and the desktop client
on multiple user PCs.

## Architecture

- `main.py` - server entrypoint that starts Uvicorn
- `app/app.py` - FastAPI application with startup lifecycle and database initialization
- `desktop_app.py` - desktop client UI with login, Pomodoro controls, and overlay
- `run_server.sh` - convenient server startup script
- `run_client.sh` - convenient client startup script
- `requirements.txt` - Python dependency list

## Installation

1. Create and activate a Python virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the backend on a separate machine

On the dedicated server machine:

```bash
./run_server.sh
```

This starts the API on `0.0.0.0:8000`, making it accessible from other computers on the network.

### Running the desktop client on user machines

On each user PC:

```bash
./run_client.sh http://<SERVER_IP>:8000
```

Alternatively, set the environment variable:

```bash
export POMODORO_HUB_API_URL="http://<SERVER_IP>:8000"
./run_client.sh
```

## Authentication and local persistence

PomodoroHub uses a local SQLite database (`./test.db`) to store user and session data.

- Users register with a username and password.
- Passwords are never stored in plain text.
- Password hashing is performed using `passlib` with the `bcrypt` algorithm.
- The hashed password is saved in the `usuarios` table in the local database.
- Login verifies the provided password against the stored bcrypt hash.

This adds an extra layer of complexity and security by ensuring that
sensitive credentials are protected even when stored locally.

## How login works

1. The client sends `POST /users/register` with `name` and `password`.
2. The backend hashes the password and creates a new user record.
3. To sign in, the client sends `POST /users/login` with the same credentials.
4. The backend checks the username and validates the password hash.
5. If successful, the user may start or stop Pomodoro sessions.

## Session management

- `POST /pomodoro/start` starts a new Pomodoro session for the authenticated user.
- `POST /pomodoro/stop` stops the current active session.
- `GET /pomodoro/active` returns all currently active Pomodoro sessions.

The desktop client polls this endpoint regularly so every connected user can see who
is actively working in real time.

## Main API endpoints

- `POST /users/register`
- `POST /users/login`
- `POST /pomodoro/start`
- `POST /pomodoro/stop`
- `GET /pomodoro/active`

## Notes

- The backend must be reachable via network from each client machine.
- The client uses `POMODORO_HUB_API_URL` or `--api-url` to connect to the backend.
- Active Pomodoro sessions are visible to all running clients.
