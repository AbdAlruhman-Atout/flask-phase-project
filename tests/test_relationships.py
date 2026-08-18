from app.extensions import db
from app.models.association import student_courses
from app.models.course import Course
from app.models.student import Student


def test_student_can_enroll_in_multiple_courses(app):
    with app.app_context():
        student = Student(
            name="Alice",
            email="alice@example.com",
        )
        course1 = Course(name="Python")
        course2 = Course(name="Flask")

        db.session.add_all([student, course1, course2])

        student.courses.extend([course1, course2])
        db.session.commit()

        assert len(student.courses) == 2
        assert course1 in student.courses
        assert course2 in student.courses

        assert student in course1.students
        assert student in course2.students


def test_deleting_student_removes_enrollments(app):
    with app.app_context():
        student = Student(
            name="Bob",
            email="bob@example.com",
        )
        course = Course(name="Databases")

        db.session.add_all([student, course])
        student.courses.append(course)
        db.session.commit()

        student_id = student.student_id
        course_id = course.id

        # Remove loaded ORM objects so deletion relies on
        # the database ON DELETE CASCADE behavior.
        db.session.expunge_all()

        student = db.session.get(Student, student_id)
        db.session.delete(student)
        db.session.commit()

        assert db.session.get(Student, student_id) is None

        # Deleting a student must not delete the course.
        assert db.session.get(Course, course_id) is not None

        rows = db.session.execute(
            db.select(student_courses).where(
                student_courses.c.student_id == student_id
            )
        ).all()

        assert rows == []


def test_deleting_course_removes_enrollments(app):
    with app.app_context():
        student = Student(
            name="Charlie",
            email="charlie@example.com",
        )
        course = Course(name="Networking")

        db.session.add_all([student, course])
        student.courses.append(course)
        db.session.commit()

        student_id = student.student_id
        course_id = course.id

        db.session.expunge_all()

        course = db.session.get(Course, course_id)
        db.session.delete(course)
        db.session.commit()

        assert db.session.get(Course, course_id) is None

        # Deleting a course must not delete the student.
        assert db.session.get(Student, student_id) is not None

        rows = db.session.execute(
            db.select(student_courses).where(
                student_courses.c.course_id == course_id
            )
        ).all()

        assert rows == []
