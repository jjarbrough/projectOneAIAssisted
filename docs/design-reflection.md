# TaskTrack Design Reflection

## Separation of Concerns & Modularity

I structured the backend around layered modules to keep responsibilities narrow and code easy to test. Configuration and security helpers live under `app/core`, while `app/db` holds SQLAlchemy primitives. The routers (`app/api/routes`) are intentionally thin; they validate transport-level concerns and hand off to service classes in `app/services`, which capture the business rules. Those services, in turn, rely on repositories (`app/repositories`) so that all database queries remain in a single layer. This design lets me stub or swap persistence implementations without touching business logic or endpoints.

On the frontend, I avoided monolithic scripts by splitting modules into clear roles: `apiClient` for HTTP concerns, `state` for local session/list/task state, `ui` for DOM rendering, and `app` to orchestrate events. This mirrors the backend layering at a smaller scale, and prevents tight coupling between transport details (fetch) and rendering logic.

## Applying TDD

I wrote the pytest suite (authentication, access control, and task lifecycle) before implementing the FastAPI app. The tests instantiate the app via a factory, override the database dependency with an isolated SQLite engine, and exercise the public HTTP contract. This forced me to think about the API signature, status codes, and error cases up front. Every backend change was driven by making the tests pass, which caught issues like authentication wiring and task ownership early. Frontend tests are not yet automated because Node tooling was unavailable in this environment, but the backend tests provide high confidence in the core domain rules the UI consumes.

## Ensuring Low Coupling & High Cohesion

Service classes depend only on repositories and settings, so they can be reused in CLI jobs or background workers without importing FastAPI. Routers inject dependencies (database sessions, current user) through FastAPI’s dependency system, keeping request context out of lower layers. Pydantic schemas own API representation, preventing data-leakage of ORM entities. On the client, state management is centralized, preventing components from directly mutating DOM based on ad-hoc data structures.

## Optional Enhancements Implemented

- **Priorities & Tagging** – Task schemas, repositories, and services were extended (test-first) to capture a priority enum, free-form tags, and deterministic list ordering via a `position` field. Frontend forms expose these attributes and display them as badges and chips.
- **Drag-and-drop Ordering** – The UI uses HTML5 drag events to reorder tasks. Drops trigger the REST `reorder` endpoint so all clients share the same persisted ordering.
- **Real-time Sync** – A lightweight `TaskNotifier` keeps track of WebSocket subscribers per list. After any mutation, routers notify the notifier (using `anyio.from_thread.run` to bridge sync code) and the frontend receives a `tasks_changed` event, refreshing data automatically.

## What I Would Improve Next

1. **Automated Frontend Tests** – Once Node is available, I would introduce Vitest or Playwright tests to cover UI interactions and API integration from the browser perspective.
2. **User Profiles & Settings** – Expose an endpoint to read the current user profile so the frontend can display accurate identity details instead of the “restored session” placeholder.
3. **Task List Sharing** – Introduce a sharing model (invites/roles) so teams can collaborate on the same lists, which would extend both the schema and authorization logic.
4. **Background Jobs** – Add scheduled jobs (e.g., email reminders for due tasks) using a task queue, demonstrating how the service/repository layers can be reused outside HTTP contexts.

