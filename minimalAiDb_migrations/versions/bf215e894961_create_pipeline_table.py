"""create pipeline table

Revision ID: bf215e894961
Revises: 
Create Date: 2023-09-04 21:49:56.664336

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'bf215e894961'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'pipeline_meta',
        sa.Column('pipeline_uuid', sa.String(500), unique=True, index=True),
        sa.Column('created_by', sa.String(500), nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('modified_by', sa.String(500)),
        sa.Column('modified_at', sa.DateTime),
        sa.PrimaryKeyConstraint('pipeline_uuid')
    )

    op.create_table(
        'pipeline_run_status',
        sa.Column('id', sa.Integer, unique=True,
                  autoincrement='auto', index=True),
        sa.Column('pipeline_uuid', sa.String(500), index=True),
        sa.Column('latest_run_status', sa.String(30)),
        sa.ForeignKeyConstraint(
            ['pipeline_uuid'], ['pipeline_meta.pipeline_uuid']),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('pipeline_meta')
    op.drop_table('pipeline_run_status')
