# Architecture and decisions

Angular/TypeScript -> Flask REST API -> PostgreSQL.

The browser maintains draft edits. Save sends a validated configuration to Flask;
PostgreSQL stores it. Report generation reads the saved database version, never an
unsaved browser draft. The source default is immutable, separate from user settings.
Restore copies the default into the saved configuration and updates the UI.

Use one demo template initially; authentication and multi-user tenancy are outside
the email's explicit scope. Store structured configuration in PostgreSQL JSONB with
schema version, configuration revision, and timestamps. Keep clinical report content
separate from layout. Stable section IDs map to content; array order controls rendering.
Five numbered sections plus legend and patient card are seven movable blocks.

PDF export is an implementation assumption based on the supplied sample. Preserve
section structure, tables, repeated headers/footers and dynamic pagination. Basic
header/footer formatting: size, color, alignment, bold, italic. Arbitrary HTML is not
accepted. The exact visual fidelity and data coverage will be documented after module 6.

Routes (implemented through module 6):
- GET /api/health: liveness, not database readiness.
- GET /api/templates/default: immutable baseline.
- GET /api/templates/current: last saved configuration, or baseline before first save.
- PUT /api/templates/current: validate and save configuration.
- POST /api/templates/current/restore: persist a fresh default copy.
- POST /api/reports: render PDF from the last saved configuration.

Validation: all seven unique known IDs exactly once, bounded non-empty headings,
bounded text and font size, enumerated alignment, hex colors, reject unknown fields.
Errors return a consistent JSON envelope; do not expose internal stack traces.

Framework compatibility: https://angular.dev/reference/versions

Template GET/PUT/restore responses wrap the layout as `configuration`, with revision,
updatedAt, and isDefault metadata. PUT accepts the bare configuration. An atomic
PostgreSQL upsert prevents first-save races and increments revision on every write.
Writes are last-write-wins; optimistic concurrency and authentication are outside
this demo's scope. Failed database operations roll back and return sanitized 503
errors. The baseline endpoint is independent of database availability.

ReportLab renders A4 reports using escaped Paragraphs, splittable LongTables, embedded
Vera fonts, and dynamic header/footer margins. Each page repeats metadata and page
numbering. Long decoration text shrinks to fit reserved regions. The report endpoint
accepts no body and reads the last saved server configuration. It returns a PDF
attachment with the revision header and no-store caching. Report content remains
synthetic and separate from preferences; fidelity limits are documented in README.
