# Implementation modules and genuine commit plan

Target budget: 8 hours total. Commit after each working module and its checks.
Do not pre-create feature commits or rewrite history to suggest work not performed.

## Starting point

Module 1 is already recorded in `e56a6ac` (`Initial_commit`). Keep that commit
unchanged and continue with module 2. The time estimates below include the existing
foundation; they are planning estimates, not a record of elapsed assessment time.
Modules 2-7 have an estimated 7 hours 15 minutes remaining.

| Module | Budget | Commit message | Completion criteria |
| --- | --- | --- | --- |
| 1. Foundation | 45 min | chore: scaffold Angular Flask and PostgreSQL workspace | Frontend shell, API health, environment examples, database service, project docs |
| 2. Defaults and persistence | 60 min | feat: add immutable report defaults and template schema | Seven section IDs, synthetic content, PostgreSQL model, real migration, default not mutated |
| 3. Template API | 75 min | feat: add validated template save load and restore APIs | Round-trip order/headings/formatting, restart persistence, useful 400/500 errors, restore |
| 4. Section builder | 75 min | feat: add draggable report sections and editable headings | Angular CDK drag/drop, stable IDs, keyboard reorder controls, loading and failure states |
| 5. Formatting and save flow | 60 min | feat: add header footer formatting and saved template flow | Formatting controls, dirty state, save feedback, refresh reload, restore confirmation |
| 6. Report generation | 90 min | feat: generate PDF reports from saved templates | Server reads last saved data, logical blocks reorder, multipage tables/header/footer, PDF download |
| 7. Verification and handoff | 75 min | test: verify core workflow and document setup | PostgreSQL integration checks, frontend build, smoke flow, README decisions/limits, GitHub handoff |

## Implementation boundaries

### Module 2: Default report and database foundation

- Define the seven stable section IDs and their default headings/order.
- Add synthetic report content based on the sample's structure, separate from layout settings.
- Add the PostgreSQL connection, configuration model, and executable migration.
- Keep an immutable baseline and return independent copies for customization.
- Verify migration against PostgreSQL and that editing a copy cannot change defaults.

### Module 3: Save, load, and restore APIs

- Implement the default/current GET routes, current PUT route, and restore POST route.
- Validate complete section membership/order, headings, and header/footer formatting.
- Persist settings, revisions, and timestamps with consistent JSON errors.
- Verify save/load round trips, persistence across application restart, invalid input,
  and restoration without changing the baseline.

### Module 4: Section editor

- Load template data through a typed Angular API service.
- Add section drag-and-drop, keyboard reorder controls, and heading inputs.
- Keep stable section IDs attached to content throughout reorder/rename operations.
- Provide loading, empty/error, and retry states with a responsive editor layout.
- Verify reorder and rename behavior in the browser and run the production build.

### Module 5: Formatting and saved-state workflow

- Add header/footer text, font size, color, alignment, bold, and italic controls.
- Add save feedback, unsaved-change indication, and restore-default interaction.
- Reload persisted configuration on reopening and handle failed saves without losing drafts.
- Verify save-refresh, formatting persistence, restore, and API failure feedback.

### Module 6: Report generation

- Render report content using the configuration read from PostgreSQL.
- Add PDF generation/download, reordered logical sections, renamed headings,
  configured headers/footers, and automatic pagination.
- Preserve tables and risk colors; inspect long tables and page boundaries visually.
- Verify that unsaved browser edits do not affect output and that restored output
  uses the original configuration. Document fidelity/content limitations honestly.

### Module 7: Integration verification and submission documentation

- Exercise the complete edit-save-refresh-generate-restore workflow.
- Complete meaningful integration/regression checks and fix any discovered defects.
- Update README with exact setup/migration commands, API details, decisions, and limitations.
- Verify setup from a clean checkout and review the final diff and commit history.
- Push to the selected GitHub repository when configured; record its link for submission.

## Commit discipline

Implement modules in order: 2 -> 3 -> 4 -> 5 -> 6 -> 7. Each module ends in a working,
reviewable state with its relevant checks completed. Stage only that module's changes
and update its status/check results here in the same commit. Use additional focused
fix commits when warranted; do not force unrelated changes into one milestone.
Never commit secrets, local environments, generated dependency folders, or the source
clinical PDF. Do not create empty milestone commits in advance.

The plan was recorded before implementation; completion evidence follows below.

## Acceptance checklist
- [x] Original report structure represented in default template.
- [x] All section contents move with their heading.
- [x] Heading changes and header/footer text/formatting persist in PostgreSQL.
- [x] Refresh/reopen loads last saved configuration.
- [x] Unsaved edits do not affect generated report.
- [x] Restore leaves immutable baseline unchanged.
- [x] Invalid API requests produce helpful errors.
- [x] Long output has no clipped rows or header/footer collisions.
- [x] Responsive layout and accessible reorder controls.
- [x] Clean checkout can be set up from README and migration scripts.
- [x] GitHub repository contains meaningful incremental commits.

Module 1 creates placeholders for later modules. Placeholder directories do not mean
those modules are implemented. Update this document as each module is completed.

## Module 1 verification
Completed: Python syntax checks, JSON configuration parsing, Flask health/404 test (1 passed), Angular production build. Dependency lockfiles included. PostgreSQL container not run because Docker is unavailable in the authoring environment. Browser interaction testing is deferred until the editor exists.

## Module 2 verification

Implemented: seven stable default sections, independent baseline/content copies,
synthetic fixtures, SQLAlchemy JSONB singleton model, and Alembic migration.
Verified PostgreSQL 18 migration upgrade, configuration round trip through a fresh
ORM session, database constraints, timezone timestamps, and default isolation.
The local project database is provisioned on desktop PostgreSQL port 5432. API routes and
payload validation remain module 3 work. Synthetic fixtures represent structure,
not the full 45-page source report or clinical recommendations.

## Module 3 verification

Implemented default/current GET, current PUT, and restore POST routes, strict
version-one validation, metadata responses, atomic upserts with revisions, and
sanitized storage errors with rollback. PostgreSQL integration checks use an isolated
schema, run the real migration, and commit saves before loading through a new Flask
application. Verified defaults before first save, order/headings/formatting round
trip, rejected saves preserving stored data, repeated saves, persisted restore, and
unchanged baseline. All 21 backend tests pass with PostgreSQL enabled. UI and PDF
work remain in modules 4-6.

## Module 4 verification

Implemented typed template loading, Angular CDK grip-based drag-and-drop, keyboard
Up/Down controls with live announcements, editable headings, a synchronized outline,
and responsive loading/error/retry/empty states. Stable IDs preserve content mapping.
Verified in headless Microsoft Edge against the running Angular/Flask application:
seven sections load; rename updates outline; keyboard and actual pointer drag reorder
without losing IDs; blank headings are flagged; refresh restores saved settings;
503/retry and empty responses render correctly; mobile width 390px has no overflow;
no browser page errors. Inspected desktop/mobile screenshots. Production build passed.
Saving and formatting remain module 5 work; PDF output remains module 6 work.

## Module 5 verification

Implemented header/footer text, size, alignment, color, bold/italic, live text
previews, save feedback, actual draft-versus-saved dirty tracking, before-unload
warning, and confirmed restore. Failed writes preserve the draft; busy states lock
editing until the response arrives. Validation prevents saving blank headings or
out-of-range/noninteger sizes. Browser checks passed for saved heading/order and
formatting after refresh, save failure with draft retained, validation, restore
cancel/failure/retry/persistence, reverted dirty state, 390px mobile width, and no
page errors. Mobile screenshot inspected and Angular production build passed.
PDF generation remains module 6 work.

## Module 6 verification

Implemented server-side saved-template PDF rendering and browser download with
busy/status/error states. Rendered all seven section types, escaped headings/text,
formatting, metadata, repeating headers/footers, dynamic page numbers, colored tables,
repeating table headers, and splitting oversized rows. Updated runtime/development
requirements and lockfile. All 25 backend tests pass with PostgreSQL enabled,
including generation after save and restore. Browser download/failure/retry checks
passed; downloaded PDF text excludes unsaved browser edits. Production build passed.
Inspected both default PDF pages and a 12-page stress-report contact sheet plus table
page detail. Synthetic content, font coverage, and long-text shrink behavior are
explicit limitations. Existing Flask on port 5000 needs restart to load the route;
a temporary port-5001 instance was used for browser download verification.

## Module 7 verification and handoff

Added a repeatable `scripts/verify.py` command, dedicated-schema browser server,
and two Playwright regressions for the complete workflow and load recovery.
Verified 25 backend tests, two headless Edge browser tests, and Angular production
build. A fresh local clone plus the Module 7 patch passed pinned Python installation,
`pip check`, `npm ci`, fresh-database migration, and the same full verification.
Browser checks cover pointer/keyboard ordering, formatting/color, saved refresh,
PDF revision/download, retained drafts, save/download/restore failure and retry,
restore cancellation/persistence, and mobile width. Fixed database connection hangs
with a five-second connect timeout and stale pooled-connection checks. Pinned the
Windows-only dependencies found during clean installation.

README now documents actual setup, test database preparation, API contracts,
technical decisions, and fidelity limits. The acceptance checklist refers to the
synthetic representative report structure, not reproduction of the original clinical
dataset. Docker was unavailable; PostgreSQL 18 was verified. Source, migrations,
verification commands, and genuine incremental commits are prepared for the configured
repository: https://github.com/SaiP598/dynamic-report-template. See verification.md
for the repeatable checks and handoff notes.
