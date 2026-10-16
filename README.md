# Dynamic Report Template

Assessment implementation using Angular/TypeScript, Python Flask, and PostgreSQL.

## Current status
Modules 1-2 complete: application scaffold, immutable default layout, seven synthetic
report content blocks, PostgreSQL JSONB model, and executable Alembic migration.
The editor, save/load APIs, and PDF generation follow in modules 3-6.

## Prerequisites
Node.js 24, npm, Python 3.12+, Docker with Compose (or local PostgreSQL 17).
Angular 21 uses TypeScript 5.9; see https://angular.dev/reference/versions.

## Setup
From the project root, copy `.env.example` to `.env` (PowerShell: `Copy-Item .env.example .env`).
The example password is for local development only.

```bash
cp .env.example .env
docker compose up -d db
python -m venv .venv
```
Activate the virtual environment:
- macOS/Linux: `source .venv/bin/activate`
- Windows PowerShell: `.venv\Scripts\Activate.ps1`

```bash
python -m pip install -r backend/requirements-lock.txt
cd backend
python -m flask --app app:create_app db upgrade
python -m flask --app app:create_app run --port 5000
```
In a second terminal:
```bash
cd frontend
npm ci
npm start
```
Open http://localhost:4200. The development proxy forwards `/api` to Flask at
127.0.0.1:5000. Health is available at http://localhost:5000/api/health.
The health endpoint does not require or verify a database connection yet.
Run migrations before starting the application. No saved configuration is seeded;
the API will fall back to the immutable baseline in module 3.

## Checks
```bash
cd backend
python -m pytest
```
```bash
cd frontend
npm run build
```

## Structure
- `frontend/src/app/core/`: API services and typed contracts.
- `frontend/src/app/features/report-builder/`: builder feature and starter screen.
- `frontend/src/app/shared/`: shared UI controls.
- `backend/app/api/`: REST endpoints.
- `backend/app/models/`: persistence models.
- `backend/app/services/`: persistence/rendering logic.
- `backend/app/validation/`: request validation.
- `backend/app/data/`: immutable defaults and synthetic fixtures.
- `backend/app/templates/`: report rendering templates.
- `backend/migrations/`: schema migration scripts.
- `backend/tests/`: backend checks.
- `docs/module-plan.md`: milestones, commit messages, acceptance checklist.
- `docs/architecture.md`: architecture and API plan.
- `references/private/`: ignored local assessment reference.

## Git workflow
The initial scaffold is committed locally. Each subsequent module gets its own real
commit after verification. No remote repository is configured yet.

After creating an empty GitHub repository, connect and push:
```bash
git remote add origin <YOUR_GITHUB_REPOSITORY_URL>
git push -u origin main
```

The original clinical PDF is not included in version control. Use synthetic patient
data for committed fixtures. See `docs/architecture.md` for scope and assumptions.

## Local Windows database for this workspace

A dedicated PostgreSQL 18 cluster was created in ignored `.local/postgres` on
127.0.0.1:55433. This workspace's ignored `.env` points to it. The existing system
service on port 5432 is independent. Do not start Compose on the same port while
this cluster is running. Other checkouts may use the Compose setup above.

From the project root, start/stop this cluster when needed:
```powershell
& 'C:\Program Files\PostgreSQL\18\bin\pg_ctl.exe' -D .local/postgres -l .local/postgres.log -o '-p 55433 -h 127.0.0.1' -w start
& 'C:\Program Files\PostgreSQL\18\bin\pg_ctl.exe' -D .local/postgres -m fast -w stop
```

The application role owns the `report_builder` database. Local administrator
credentials are kept in ignored `.local/admin-password`. Neither `.local` nor
`.env` belongs in Git. JSONB changes should replace the configuration object;
SQLAlchemy does not track nested in-place edits automatically.

For PostgreSQL tests, set `TEST_DATABASE_URL` to a dedicated migrated test database
before running pytest. Without it, database tests are explicitly skipped.
