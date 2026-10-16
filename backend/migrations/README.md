# Database migrations

From `backend`, with the virtual environment activated and root `.env` configured:

```bash
python -m flask --app app:create_app db upgrade
python -m flask --app app:create_app db current
```

Revision `175ceb527563` creates `template_configurations`, a singleton saved layout
with JSONB configuration, schema version, revision, and timezone-aware timestamps.
The immutable default remains in Python source; the migration does not seed it.

`db downgrade` removes the table and its saved configuration. Use downgrade only
against disposable databases or after a backup. Do not substitute `create_all` for
migrations. Detailed payload validation and revision updates arrive in module 3.
