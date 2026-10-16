"""Saved template operations; PostgreSQL upsert serializes competing writes."""
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert

from ..data.defaults import get_default_configuration
from ..extensions import db
from ..models import TemplateConfiguration


def serialize_template(row):
    if row is None:
        return {"configuration": get_default_configuration(), "revision": 0,
                "updatedAt": None, "isDefault": True}
    return {"configuration": row.configuration, "revision": row.revision,
            "updatedAt": row.updated_at.isoformat(),
            "isDefault": row.configuration == get_default_configuration()}


def load_current():
    return serialize_template(db.session.get(TemplateConfiguration, 1))


def save_configuration(configuration):
    table = TemplateConfiguration.__table__
    statement = insert(TemplateConfiguration).values(id=1, schema_version=1, revision=1,
                                     configuration=configuration)
    statement = statement.on_conflict_do_update(
        index_elements=[table.c.id],
        set_={"configuration": statement.excluded.configuration,
              "revision": table.c.revision + 1, "updated_at": func.now()},
    ).returning(TemplateConfiguration)
    row = db.session.execute(statement, execution_options={"populate_existing": True}).scalar_one()
    result = serialize_template(row)
    db.session.commit()
    return result
