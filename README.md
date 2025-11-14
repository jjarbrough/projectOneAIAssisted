# TaskTrack

TaskTrack is a full-stack task management application built with a Test-Driven Development workflow. It provides secure user authentication, RESTful APIs for managing task lists and tasks, and a lightweight frontend that consumes the API.

## Features

- User registration and login with hashed passwords and JWT access tokens.
- CRUD operations for task lists and tasks with per-user access control.
- Status management for tasks (`pending`, `in_progress`, `completed`).
- Modular FastAPI backend with SQLAlchemy ORM and SQLite persistence.
- Task priorities (low/medium/high), tagging, and manual drag-and-drop ordering.
- Real-time task refresh via WebSockets so multiple clients stay in sync.
- Vanilla JavaScript frontend that consumes the REST API.
- Comprehensive backend unit tests covering authentication and task lifecycle.

## Project Structure

```
TaskTrack/
├── backend/
│   ├── app/
│   │   ├── api/              # FastAPI routers and dependencies
│   │   ├── core/             # Configuration and security utilities
│   │   ├── db/               # SQLAlchemy session and models
│   │   ├── repositories/     # Data-access layer
│   │   ├── schemas/          # Pydantic request/response models
│   │   └── services/         # Business logic
│   ├── tests/                # Pytest test suite written first (TDD)
│   ├── requirements.txt
│   └── pytest.ini
├── frontend/
│   ├── index.html            # Single-page UI
│   ├── styles/main.css
│   └── scripts/              # Modular JS (API client, state, UI orchestration)
└── docs/
    └── design-reflection.md  # Architecture notes and improvement ideas
```

## Backend Setup

> Requires Python 3.11+ (the project was developed with Python 3.13 on Windows).

```powershell
cd backend
py -3 -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Run the API

```powershell
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

### Run Tests

All backend functionality was developed with TDD. The test suite covers authentication, access control, and task lifecycle.

```powershell
venv\Scripts\activate
pytest
```

## API Overview

| Method | Endpoint                    | Auth | Description                     |
|--------|-----------------------------|------|---------------------------------|
| POST   | `/api/register`             | ❌   | Create a new user and token     |
| POST   | `/api/login`                | ❌   | Authenticate and receive token  |
| GET    | `/api/lists`                | ✅   | List user's task lists          |
| POST   | `/api/lists`                | ✅   | Create a task list              |
| GET    | `/api/lists/{list_id}/tasks`| ✅   | Get tasks for a list            |
| POST   | `/api/lists/{list_id}/tasks`| ✅   | Create task in a list           |
| PUT    | `/api/tasks/{task_id}`      | ✅   | Update task (title/status/etc.) |
| DELETE | `/api/tasks/{task_id}`      | ✅   | Delete task                     |
| PUT    | `/api/lists/{list_id}/tasks/reorder` | ✅ | Persist drag-and-drop order |

All authenticated routes expect a header: `Authorization: Bearer <token>`.

### Real-time updates

- WebSocket endpoint: `ws://localhost:8000/api/ws/lists/{list_id}?token=<JWT>`
- The frontend automatically connects and refreshes tasks when any client creates, updates, deletes, or reorders items in the same list.

## Frontend Usage

The frontend is a modular, dependency-free JavaScript application. It can be served from any static HTTP server or opened directly in a browser once the API is running.

```powershell
cd frontend
python -m http.server 5173
```

Then navigate to `http://localhost:5173` (update the port if you prefer another). The frontend communicates with the API at `http://localhost:8000`.

### One-click launch scripts (Windows)

For quicker local runs, the repository includes helper scripts in the project root:

- `start_backend.bat` – prepares the virtual environment (if needed), installs backend dependencies, and starts Uvicorn on `http://127.0.0.1:8000`.
- `start_frontend.bat` – serves the static frontend on `http://127.0.0.1:5173`.
- `start_all.bat` – opens two Command Prompt windows and runs both scripts.

Double-click the desired script or run it from `cmd.exe`. Stop the servers with `CTRL+C` in their respective windows.

**Main Screens**

- **Authentication panel**: toggle between Login and Register tabs.
- **Lists sidebar**: create new task lists, select an active list, and log out.
- **Tasks panel**: create, tag, prioritise, reorder (drag-and-drop), mark complete, and delete tasks for the selected list. A live indicator shows when the WebSocket connection is active.

## Design Highlights

- Clear separation of concerns: configuration, security, data access, services, and routing live in dedicated modules.
- Repository and service layers remove direct database access from routers, aiding testability.
- FastAPI dependency overrides in tests provide isolated, in-memory databases.
- Frontend uses modular ES modules (`apiClient`, `state`, `ui`, `app`) for low coupling.
- CORS middleware is enabled so the browser-based frontend can call the API.
- WebSocket notifier keeps all open clients synchronized after task mutations without full page reloads.

## Future Improvements

- Add automated frontend tests (e.g., Playwright or Vitest) once Node tooling is available.
- Persist user preferences (e.g., default list filters, theme) and surface task analytics.
- Replace the static frontend build with a React/Vite SPA when Node tooling is accessible.

---

See `docs/design-reflection.md` for an in-depth discussion of design decisions and improvement areas.

"# projectOneAIAssisted" 
