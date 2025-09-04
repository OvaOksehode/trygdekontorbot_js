"""Changed Company owner default field

Revision ID: 652e6fbf9c81
Revises: 
Create Date: 2025-09-04 08:32:06.001809

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '652e6fbf9c81'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Use batch_alter_table to safely alter columns in SQLite
    with op.batch_alter_table('company', schema=None) as batch_op:
        batch_op.alter_column(
            'owner',
            existing_type=sa.Integer(),
            nullable=False,
            existing_nullable=False,
            unique=True  # add the unique constraint
        )

def downgrade():
    with op.batch_alter_table('company', schema=None) as batch_op:
        batch_op.alter_column(
            'owner',
            existing_type=sa.Integer(),
            nullable=False,
            existing_nullable=False,
            unique=False
        )