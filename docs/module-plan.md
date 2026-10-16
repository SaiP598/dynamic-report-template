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

This planning update does not implement or complete modules 2-7.

## Acceptance checklist
- [ ] Original report structure represented in default template.
- [ ] All section contents move with their heading.
- [ ] Heading changes and header/footer text/formatting persist in PostgreSQL.
- [ ] Refresh/reopen loads last saved configuration.
- [ ] Unsaved edits do not affect generated report.
- [ ] Restore leaves immutable baseline unchanged.
- [ ] Invalid API requests produce helpful errors.
- [ ] Long output has no clipped rows or header/footer collisions.
- [ ] Responsive layout and accessible reorder controls.
- [ ] Clean checkout can be set up from README and migration scripts.
- [ ] GitHub repository contains meaningful incremental commits.

Module 1 creates placeholders for later modules. Placeholder directories do not mean
those modules are implemented. Update this document as each module is completed.

## Module 1 verification
Completed: Python syntax checks, JSON configuration parsing, Flask health/404 test (1 passed), Angular production build. Dependency lockfiles included. PostgreSQL container not run because Docker is unavailable in the authoring environment. Browser interaction testing is deferred until the editor exists.

## Module 2 verification

Implemented: seven stable default sections, independent baseline/content copies,
synthetic fixtures, SQLAlchemy JSONB singleton model, and Alembic migration.
Verified PostgreSQL 18 migration upgrade, configuration round trip through a fresh
ORM session, database constraints, timezone timestamps, and default isolation.
The local project database is provisioned separately on port 55433. API routes and
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
