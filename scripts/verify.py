"""Run PostgreSQL tests, production build, and isolated browser regression checks."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
import uuid

from dotenv import dotenv_values
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--test-database", help="Derive a test database URL from root .env; database must already exist")
    parser.add_argument("--browser", choices=["chromium", "msedge", "chrome"], default="chromium")
    parser.add_argument("--skip-browser", action="store_true")
    args = parser.parse_args()
    url = os.getenv("TEST_DATABASE_URL")
    if args.test_database:
        source = dotenv_values(ROOT / ".env").get("DATABASE_URL")
        if not source:
            parser.error("Root .env must contain DATABASE_URL.")
        url = make_url(source).set(database=args.test_database).render_as_string(hide_password=False)
        if make_url(source).database == args.test_database:
            parser.error("Choose a separate test database.")
    if not url:
        parser.error("Set TEST_DATABASE_URL to a dedicated PostgreSQL database, or pass --test-database.")
    env = {**os.environ, "TEST_DATABASE_URL": url, "DATABASE_URL": url,
           "E2E_PYTHON": sys.executable, "E2E_BROWSER": args.browser}
    npm = shutil.which("npm.cmd") or shutil.which("npm")
    if not npm:
        parser.error("npm is required.")
    def run(command, cwd):
        subprocess.run(command, cwd=cwd, env=env, check=True)
    # Bootstrap the dedicated database with the actual migration before integration tests.
    sys.path.insert(0, str(ROOT / "backend"))
    from app import create_app
    from flask_migrate import upgrade
    with create_app({"DATABASE_URL": url}).app_context():
        upgrade()
    run([sys.executable, "-m", "pytest", "-q"], ROOT / "backend")
    run([npm, "run", "build"], ROOT / "frontend")
    if not args.skip_browser:
        schema = "e2e_" + uuid.uuid4().hex
        engine = create_engine(url)
        with engine.begin() as connection:
            connection.execute(text(f'CREATE SCHEMA "{schema}"'))
        env["E2E_SCHEMA"] = schema
        try:
            run([npm, "run", "test:e2e"], ROOT / "frontend")
        finally:
            with engine.begin() as connection:
                connection.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
            engine.dispose()
    print("Verification complete.")


if __name__ == "__main__":
    main()
