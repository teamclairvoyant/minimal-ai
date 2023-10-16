"""creating initial table

Revision ID: bb829d2b3b61
Revises: 
Create Date: 2023-09-26 19:25:19.598281

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'bb829d2b3b61'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('pipeline_execution',
                    sa.Column('id', sa.Integer(),
                              autoincrement=True, nullable=False),
                    sa.Column('trigger', sa.Enum(
                        'MANUAL', 'SCHEDULED', name='runstatus'), nullable=False),
                    sa.Column('pipeline_uuid', sa.String(
                        length=255), nullable=False),
                    sa.Column('execution_date', sa.DateTime(
                        timezone=True), nullable=False),
                    sa.Column('status', sa.Enum('COMPLETED',
                                                'FAILED', 'CANCELLED', 'RUNNING', name='runstatus'), nullable=False),
                    sa.PrimaryKeyConstraint('id')
                    )


def downgrade() -> None:
    op.drop_table('pipeline_execution')
