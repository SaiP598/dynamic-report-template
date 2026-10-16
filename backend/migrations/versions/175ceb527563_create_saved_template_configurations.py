"""create saved template configurations

Revision ID: 175ceb527563
Revises:
Create Date: 2026-10-16 08:49:12.587986

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '175ceb527563'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('template_configurations',
    sa.Column('id', sa.SmallInteger(), autoincrement=False, nullable=False),
    sa.Column('schema_version', sa.SmallInteger(), nullable=False),
    sa.Column('revision', sa.Integer(), nullable=False),
    sa.Column('configuration', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("jsonb_typeof(configuration) = 'object'", name='configuration_object'),
    sa.CheckConstraint('id = 1', name='single_demo_template'),
    sa.CheckConstraint('revision >= 1', name='positive_revision'),
    sa.CheckConstraint('schema_version = 1', name='supported_schema_version'),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('template_configurations')
