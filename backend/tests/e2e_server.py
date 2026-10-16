"""Private verification server, launched only by scripts/verify.py."""
import os
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import create_app
from flask_migrate import upgrade

schema = os.environ.get("E2E_SCHEMA", "")
if not re.fullmatch(r"e2e_[0-9a-f]{32}", schema):
    raise SystemExit("Launch browser checks through scripts/verify.py.")
app = create_app({
    "DATABASE_URL": os.environ["TEST_DATABASE_URL"],
    "SQLALCHEMY_ENGINE_OPTIONS": {"connect_args": {"options": f"-csearch_path={schema}"}},
})
with app.app_context():
    upgrade()
app.run(host="127.0.0.1", port=5002, use_reloader=False)
