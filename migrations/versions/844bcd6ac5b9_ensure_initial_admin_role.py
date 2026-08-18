"""ensure initial admin role

Revision ID: 844bcd6ac5b9
Revises: efcb8f0f6625
Create Date: 2026-08-18 13:48:02.377495

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '844bcd6ac5b9'
down_revision = 'efcb8f0f6625'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        UPDATE users
        SET role = 'admin'
        WHERE id = (
            SELECT MIN(id)
            FROM users
        )
        AND NOT EXISTS (
            SELECT 1
            FROM users
            WHERE role = 'admin'
        )
        """
    )

    pass


def downgrade():
    pass
