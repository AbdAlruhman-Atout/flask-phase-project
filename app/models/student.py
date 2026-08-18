from app.extensions import db
from app.models.association import student_courses


class Student(db.Model):
    __tablename__ = "students"

    student_id = db.Column(
        db.Integer,
        primary_key=True,
    )

    name = db.Column(
        db.String(100),
        nullable=False,
    )

    email = db.Column(
        db.String(255),
        unique=True,
        nullable=False,
    )

    grades = db.Column(
        db.String(255),
        nullable=False,
        default="",
    )

    courses = db.relationship(
        "Course",
        secondary=student_courses,
        back_populates="students",
        passive_deletes=True,
    )

    def get_grades(self):
        if not self.grades:
            return []

        return [
            float(grade.strip())
            for grade in self.grades.split(",")
            if grade.strip()
        ]

    @property
    def average(self):
        grades = self.get_grades()

        if not grades:
            return 0.0

        return round(sum(grades) / len(grades), 2)
