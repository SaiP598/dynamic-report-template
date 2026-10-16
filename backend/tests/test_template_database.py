"""Run only against a dedicated migrated database via TEST_DATABASE_URL."""
import os

import pytest
from sqlalchemy.exc import IntegrityError

from app import create_app
from app.data.defaults import get_default_configuration
from app.extensions import db
from app.models import TemplateConfiguration

DATABASE_URL = os.getenv("TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(not DATABASE_URL, reason="Set TEST_DATABASE_URL to a migrated test database")


def test_postgres_roundtrip_and_constraints():
    app = create_app({"TESTING": True, "DATABASE_URL": DATABASE_URL})
    with app.app_context():
        # Bind an outer transaction so the test never leaves a saved template behind.
        connection = db.engine.connect()
        transaction = connection.begin()
        from sqlalchemy.orm import Session
        session = Session(bind=connection, join_transaction_mode="create_savepoint")
        try:
            configuration = get_default_configuration()
            configuration["sections"].reverse()
            configuration["header"]["text"] = "Saved header"
            row = TemplateConfiguration(configuration=configuration)
            session.add(row)
            session.commit()
            session.close()
            # A fresh ORM session must load the stored JSONB rather than cached state.
            session = Session(bind=connection, join_transaction_mode="create_savepoint")
            saved = session.get(TemplateConfiguration, 1)
            assert saved.configuration == configuration
            assert saved.schema_version == saved.revision == 1
            assert saved.created_at.tzinfo is not None
            assert saved.updated_at.tzinfo is not None
            assert get_default_configuration()["header"]["text"] != "Saved header"
            session.add(TemplateConfiguration(id=2, configuration={}))
            with pytest.raises(IntegrityError):
                session.flush()
            session.rollback()
        finally:
            session.close()
            transaction.rollback()
            connection.close()
