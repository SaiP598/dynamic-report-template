# Verification and handoff

Verification date: 16 October 2026 (IST).

## Repeatable checks

Follow README setup, create a separate `report_builder_test` database, activate the
Python environment, and run from the project root:

```bash
python scripts/verify.py --test-database report_builder_test --browser msedge
```

Omit `--browser msedge` for installed Playwright Chromium. The script applies the
actual migration to the dedicated test database, runs 25 backend checks, builds
Angular, then starts private Flask/Angular servers on 5002/4202. Browser writes use
a randomly named schema, which the parent verification process drops in a finally
block. No app preferences in the main database are changed.

## Results

- 25 backend tests passed with PostgreSQL enabled.
- Two browser regression tests passed in headless Microsoft Edge.
- Angular production build passed.
- A fresh local Git clone plus the pending Module 7 patch was verified with a new
  Python virtual environment, pinned pip installation, `pip check`, `npm ci`, a
  newly created PostgreSQL database, and the full backend/build/browser command.
  The disposable database was removed after verification.
- The fresh npm install reported zero known vulnerabilities. Docker itself was
  unavailable and its startup path was not executed.
- Earlier PDF visual checks inspected both default pages and a 12-page stress
  report; PDFs use synthetic fixtures, as documented.

## Coverage

- Immutable default/content copies, database constraints, JSONB round trips,
  revision/timestamp metadata, and storage-independent defaults.
- Complete payload validation, malformed/non-JSON requests, unknown/missing fields,
  invalid types, duplicate sections, bounds, and sanitized rollback errors.
- Real migrations, save/reload through a fresh Flask application, invalid saves
  leaving data unchanged, restore persistence, and immutable baseline preservation.
- Saved/restore PDFs, escaped markup, reversed sections and renamed headings,
  repeated metadata and decorations, long tables, oversized rows, and extreme text.
- Browser pointer and keyboard reorder, stable IDs, renamed headings, formatting,
  save-refresh, PDF attachment/revision, retained drafts, failed save and retry,
  validation blocking, restore confirmation/cancel, persisted restore, and mobile width.
- API-load failure followed by successful retry.

The browser test waits for CDK preview/placeholder removal before checking stable
section IDs; animation-only nodes are not report sections. Prior module checks also
covered restore/download failure and retry, and inspected default/stress PDF pages.

## Manual review

1. Follow README setup with a migrated database and start both application servers.
2. Edit, save, refresh, and generate; inspect changed headings/order/formatting.
3. Generate with unsaved changes and verify they are excluded from the PDF.
4. Restore defaults and verify both editor and generated output after refresh.
5. Review table continuation and header/footer separation in a long report.
6. Inspect keyboard focus/reorder announcements and a narrow mobile viewport.

## Material limitations

The output represents the reference report's section structure using synthetic data.
The original 45-page clinical dataset, patient identifiers, and logos are not shipped.
There is one shared demo template with last-write-wins edits, no authentication or
clinical calculation, and no guarantee for non-Latin fonts. Long decorations shrink
to fit. Docker was unavailable; PostgreSQL 18 was used for integration verification.

## Submission

Repository: https://github.com/SaiP598/dynamic-report-template

Source includes README setup, executable database migrations, architecture/decisions,
limitations, backend checks, and repeatable browser regression tests. No email is
sent automatically. The repository link can be shared with the assessment team.
