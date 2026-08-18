"""add cascade delete to student course relationship

Revision ID: 39de799ce5ae
Revises: 51e93d39ed03
Create Date: 2026-08-18 11:53:23.963426
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "39de799ce5ae"
down_revision = "51e93d39ed03"
branch_labels = None
depends_on = None


def upgrade():
    # SQLite cannot directly alter unnamed foreign-key constraints,
    # so recreate the association table with ON DELETE CASCADE.
    op.create_table(
        "student_courses_new",
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("course_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["student_id"],
            ["students.student_id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["course_id"],
            ["courses.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("student_id", "course_id"),
    )

    op.execute(
        """
        INSERT INTO student_courses_new (student_id, course_id)
        SELECT student_id, course_id
        FROM student_courses
        """
    )

    op.drop_table("student_courses")
    op.rename_table("student_courses_new", "student_courses")


def downgrade():
    # Recreate the original table without ON DELETE CASCADE.
    op.create_table(
        "student_courses_old",
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("course_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["student_id"],
            ["students.student_id"],
        ),
        sa.ForeignKeyConstraint(
            ["course_id"],
            ["courses.id"],
        ),
        sa.PrimaryKeyConstraint("student_id", "course_id"),
    )

    op.execute(
        """
        INSERT INTO student_courses_old (student_id, course_id)
        SELECT student_id, course_id
        FROM student_courses
        """
    )

    op.drop_table("student_courses")
    op.rename_table("student_courses_old", "student_courses")
