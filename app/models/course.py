from app.extensions import db
from app.models.association import student_courses


class Course(db.Model):
    __tablename__ = "courses"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    name = db.Column(
        db.String(100),
        unique=True,
        nullable=False,
    )

    students = db.relationship(
        "Student",
        secondary=student_courses,
        back_populates="courses",
    )
