from app import create_app
from app.extensions import db
from app.models import Course, Student


app = create_app()


def seed_database():
    student = db.session.get(Student, 1001)

    if student is None:
        student = Student(
            student_id=1001,
            name="Alice",
            email="alice@example.com",
            grades="90,85,78",
        )
        db.session.add(student)

    python_course = db.session.execute(
        db.select(Course).where(Course.name == "Python Programming")
    ).scalar_one_or_none()

    if python_course is None:
        python_course = Course(name="Python Programming")
        db.session.add(python_course)

    database_course = db.session.execute(
        db.select(Course).where(Course.name == "Database Systems")
    ).scalar_one_or_none()

    if database_course is None:
        database_course = Course(name="Database Systems")
        db.session.add(database_course)

    db.session.flush()

    if python_course not in student.courses:
        student.courses.append(python_course)

    if database_course not in student.courses:
        student.courses.append(database_course)

    db.session.commit()


if __name__ == "__main__":
    with app.app_context():
        seed_database()
        print("Database seeded successfully.")
