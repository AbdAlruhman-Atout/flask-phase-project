from app.extensions import db


student_courses = db.Table(
    "student_courses",
    db.Column(
        "student_id",
        db.Integer,
        db.ForeignKey("students.student_id"),
        primary_key=True,
    ),
    db.Column(
        "course_id",
        db.Integer,
        db.ForeignKey("courses.id"),
        primary_key=True,
    ),
)
