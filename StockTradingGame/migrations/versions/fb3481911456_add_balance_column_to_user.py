"""Add balance column to user

Revision ID: fb3481911456
Revises: 
Create Date: 2024-11-05 18:58:46.998329

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision = 'fb3481911456'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Check if the 'balance' column already exists
    conn = op.get_bind()
    result = conn.execute(text("PRAGMA table_info(user);"))
    columns = [row[1] for row in result]  # row[1] holds the column name

    # If 'balance' column doesn't exist, add it
    if 'balance' not in columns:
        with op.batch_alter_table('user', schema=None) as batch_op:
            batch_op.add_column(sa.Column('balance', sa.Float(), nullable=True))


def downgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('balance')
