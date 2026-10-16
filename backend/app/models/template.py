"""Saved layout for the single assessment demo template."""
from sqlalchemy import CheckConstraint, func
from sqlalchemy.dialects.postgresql import JSONB

from ..extensions import db


class TemplateConfiguration(db.Model):
    __tablename__ = "template_configurations"
    __table_args__ = (
        CheckConstraint("id = 1", name="single_demo_template"),
        CheckConstraint("schema_version = 1", name="supported_schema_version"),
        CheckConstraint("revision >= 1", name="positive_revision"),
        CheckConstraint("jsonb_typeof(configuration) = 'object'", name="configuration_object"),
    )

    id = db.Column(db.SmallInteger, primary_key=True, autoincrement=False, default=1)
    schema_version = db.Column(db.SmallInteger, nullable=False, default=1)
    revision = db.Column(db.Integer, nullable=False, default=1)
    configuration = db.Column(JSONB, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False,
                           server_default=func.now(), onupdate=func.now())
