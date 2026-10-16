# Dynamic Report Template

Angular/TypeScript + Flask + PostgreSQL assessment application. Arrange seven report
sections, rename headings, format headers/footers, save preferences, restore the
default, and download a PDF generated from the last saved configuration.

All seven implementation modules are complete. The report uses the email PDF only
as a visual design reference: US Letter sizing, teal title/section styling,
patient/specimen/provider columns, colored medication tables, and a two-column
laboratory footer. Patient and clinical content is synthetic or a generic placeholder. Proove Genomics branding is retained as requested.
The original attachment, patient data, clinical results, and real institutional
contact details are not used by the application. A standalone Proove logo and the
company name are retained as requested.

## Prerequisites

- Node.js 24 and npm (Angular 21 / TypeScript 5.9).
- Python 3.12 or newer.
- PostgreSQL 17 or 18, or Docker with Compose for the PostgreSQL 17 service.
- Chromium for browser checks, or an installed Microsoft Edge / Google Chrome.

## Setup from a clean checkout

```bash
git clone https://github.com/SaiP598/dynamic-report-template.git
cd dynamic-report-template
cp .env.example .env
```

On PowerShell use `Copy-Item .env.example .env` instead of `cp`. For an existing
checkout, preserve your working `.env`. Set development credentials and ensure
`DATABASE_URL` matches the database, port, username, and password.

No reference attachment or clinical dataset is needed to run the project.

Start PostgreSQL with Compose:

```bash
docker compose up -d db
```

Alternatively provision a local database and role using your PostgreSQL administrator,
then set `DATABASE_URL` to `postgresql+psycopg://USER:PASSWORD@HOST:PORT/DATABASE`.
Percent-encode reserved URL characters in credentials. Do not start Compose if
another database already occupies its configured port.

Create and activate a virtual environment:

```bash
python -m venv .venv
```

- PowerShell: `.venv\Scripts\Activate.ps1`
- macOS/Linux: `source .venv/bin/activate`

Install dependencies, apply the migration, and start Flask:

```bash
python -m pip install -r backend/requirements-lock.txt
cd backend
python -m flask --app app:create_app db upgrade
python -m flask --app app:create_app run --host 127.0.0.1 --port 5000
```

In a second terminal, from the project root:

```bash
cd frontend
npm ci
npm start
```

Open http://localhost:4200. The development proxy sends `/api` requests to Flask on
127.0.0.1:5000. Restart Flask after backend changes unless running with `--debug`.
The Angular dev server rebuilds frontend changes automatically.

## Try the complete workflow

1. Open the editor. Before the first save, it loads the immutable baseline.
2. Drag a dotted grip, or use keyboard-accessible Up/Down buttons, to move sections.
3. Rename headings. Section IDs keep each section's content attached to its heading.
4. Edit header/footer text, font size, alignment, color, bold, and italic; inspect
   the text previews. Blank text is allowed; blank section headings are not.
5. Select **Save template**. The unsaved indicator clears and the revision advances.
6. Refresh or reopen the editor; the saved settings return from PostgreSQL.
7. Make an unsaved change, then select **Download PDF**. The PDF still uses the
   last saved configuration; the draft remains untouched in the editor.
8. Select **Restore default**, cancel to keep your draft, or confirm to restore
   and persist the baseline. Refresh and download again to verify the default.

Failed save/restore/download requests preserve the draft and support retry. Editing
is locked during save/restore. Leaving with unsaved edits triggers the browser's
standard warning. Reverting edits clears the unsaved state.

## Tests and verification

The lockfile includes pytest and pypdf for reproducible checks. Fast backend checks:

```bash
cd backend
python -m pytest -q
```

Without `TEST_DATABASE_URL`, PostgreSQL integration tests are explicitly skipped.
For the full verification, first create a **separate, empty test database** owned
by the application role. With Compose (from the project root):

```bash
docker compose exec db sh -c 'createdb -U "$POSTGRES_USER" report_builder_test'
```

Do this once; an already-existing test database need not be recreated. For a local
PostgreSQL installation, use your administrator to create `report_builder_test`
with owner `report_builder`. Do not point verification at a database holding real data.

Install the browser once:

```bash
cd frontend
npx playwright install chromium
cd ..
```

With the Python virtual environment activated, from the project root:

```bash
python scripts/verify.py --test-database report_builder_test
```

The command derives the test connection from `.env`, applies migrations, runs all
26 backend tests, builds Angular, and runs two browser workflow tests. It uses
ports **5002 and 4202**, with a temporary database schema cleaned up afterward.
Your application on ports 5000/4200 and its saved layout remain independent.
Use `--browser msedge` or `--browser chrome` to use an installed browser instead
of downloading Chromium. `--skip-browser` runs backend checks and the production
build only. Alternatively set `TEST_DATABASE_URL` and omit `--test-database`.

Failure traces/screenshots are written under ignored `frontend/test-results/`.
See [architecture notes](docs/architecture.md) for implementation and verification details.

## API

| Method | Route | Behavior |
| --- | --- | --- |
| GET | `/api/health` | Liveness only; does not verify database availability |
| GET | `/api/templates/default` | Immutable baseline; no database access |
| GET | `/api/templates/current` | Last saved layout, or baseline before first save |
| PUT | `/api/templates/current` | Validate and persist the complete layout |
| POST | `/api/templates/current/restore` | Persist a fresh baseline; no request body |
| POST | `/api/reports` | PDF attachment using saved layout; no request body |

Template responses contain `configuration`, `revision`, `updatedAt`, and `isDefault`.
PUT accepts the **bare configuration**, not the response envelope. Revision zero
and a null timestamp indicate the baseline before its first save. `isDefault`
compares the saved layout to the baseline. Example usage:

```javascript
const current = await fetch('/api/templates/current').then(r => r.json());
current.configuration.sections[0].heading = 'My heading';
await fetch('/api/templates/current', {
  method: 'PUT', headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(current.configuration)
});
```

Validation requires schema version 1, all seven known section IDs exactly once,
nonblank headings up to 120 characters, header/footer text up to 1000 characters,
integer font sizes 6-36, boolean bold/italic, left/center/right alignment, and
`#RRGGBB` colors. Unknown fields are rejected. Text is escaped in PDF rendering.

Errors use `{"error":{"code":"...","message":"..."}}`. Invalid configuration
or malformed JSON returns 400; unsupported JSON content types return 415; oversized
bodies return 413. Storage failures roll back and return sanitized 503 errors.
Database connections time out after five seconds. Unexpected errors return 500.

PDF responses include `X-Template-Revision` and `Cache-Control: no-store` and download
as `dynamic-report.pdf`. Generation rejects client layouts; save before generating.

## Decisions and limitations

- PostgreSQL JSONB stores layout preferences separately from synthetic report content.
  Stable IDs associate headings and order with content. The baseline lives in source
  and is copied, never overwritten. No saved row is seeded during migration.
- Atomic upsert increments revisions on saves/restores. Concurrent tabs use
  **last-write-wins**; revisions are metadata rather than optimistic locks.
- Single shared demo template; authentication, multi-user tenancy, and edit history
  are outside scope. The dev-server setup is intended for local assessment review.
- ReportLab constructs the reference-inspired visual format using only synthetic
  fixtures. It never opens, copies, or imports the source PDF. Templates carry
  layout preferences, not original patient records or clinical content.
- PDFs use US Letter pages, numbered section discs, teal title strips, three metadata
  columns, green/amber/red medication columns, and two footer columns. Pagination
  follows the placeholder content, rather than copying the original 45 pages.
- Header/footer text and formatting remain editable. Long text shrinks into its
  reserved space; the text preview is not an exact page preview. Embedded Vera fonts
  support Latin text; arbitrary scripts and emoji are not guaranteed.
- Demo labels and synthetic fixture values are examples, not clinical calculations
  or original report results. Future real-data integrations would be separate work.
- Docker execution was unavailable in the authoring environment; migrations and
  integration checks were verified against local PostgreSQL 18.

## Project structure

- `frontend/src/app/core/`: typed models and HTTP services.
- `frontend/src/app/features/report-builder/`: editor and saved-state workflow.
- `frontend/e2e/`: browser regression tests.
- `backend/app/api/`: REST endpoints.
- `backend/app/data/`: immutable defaults and synthetic content.
- `backend/app/models/`: saved layout model.
- `backend/app/services/`: persistence and format-only PDF rendering.
- `backend/app/validation/`: strict configuration validation.
- `backend/migrations/`: executable Alembic migration.
- `backend/tests/`: unit/integration checks and private browser-test server.
- `scripts/verify.py`: full verification entry point.
- `docs/`: architecture, module history, and handoff evidence.

## Existing Windows workspace database

This author's workspace uses the PostgreSQL 18 desktop service on
127.0.0.1:5432, with `.env` already configured (`report_builder` / `1234`,
database `report_builder`). Saved template tables were migrated here from the
older ignored `.local/postgres` cluster.

Connect with:

```powershell
& 'C:\Program Files\PostgreSQL\18\bin\psql.exe' -h 127.0.0.1 -p 5432 -U report_builder -d report_builder
```

Fresh checkouts should follow the general setup above. `.env`, `.local`, virtual
environments, dependency folders, browser artifacts, and the clinical reference
PDF remain ignored.

## Handoff

Repository: https://github.com/SaiP598/dynamic-report-template

The initial scaffold and each subsequent module have separate implementation
commits. See the Git commit history and [architecture](docs/architecture.md).
The application uses synthetic fixtures and generic data labels, with the explicitly
requested Proove company name and logo.
No original PDF is required or read at runtime. Source-derived clinical PDF/image
copies created during the earlier fidelity experiment have been removed from the
project. To adopt the new generic labels in an existing saved layout, select
**Restore default** and confirm; custom settings otherwise remain available.
