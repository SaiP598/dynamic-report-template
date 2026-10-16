# Implementation modules and genuine commit plan

Target budget: 8 hours total. Commit after each working module and its checks.
Do not pre-create feature commits or rewrite history to suggest work not performed.

| Module | Budget | Commit message | Completion criteria |
| --- | --- | --- | --- |
| 1. Foundation | 45 min | chore: scaffold Angular Flask and PostgreSQL workspace | Frontend shell, API health, environment examples, database service, project docs |
| 2. Defaults and persistence | 60 min | feat: add immutable report defaults and template schema | Seven section IDs, synthetic content, PostgreSQL model, real migration, default not mutated |
| 3. Template API | 75 min | feat: add validated template save load and restore APIs | Round-trip order/headings/formatting, restart persistence, useful 400/500 errors, restore |
| 4. Section builder | 75 min | feat: add draggable report sections and editable headings | Angular CDK drag/drop, stable IDs, keyboard reorder controls, loading and failure states |
| 5. Formatting and save flow | 60 min | feat: add header footer formatting and saved template flow | Formatting controls, dirty state, save feedback, refresh reload, restore confirmation |
| 6. Report generation | 90 min | feat: generate PDF reports from saved templates | Server reads last saved data, logical blocks reorder, multipage tables/header/footer, PDF download |
| 7. Verification and handoff | 75 min | test: verify core workflow and document setup | PostgreSQL integration checks, frontend build, smoke flow, README decisions/limits, GitHub handoff |

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
