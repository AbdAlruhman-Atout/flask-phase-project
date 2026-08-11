students = []


def add_student(name, student_id, email, grades):
    student = {
        "name": name,
        "student_id": student_id,
        "email": email,
        "grades": grades,
    }

    students.append(student)
    return student


def get_all_students():
    return students


def get_student_by_id(student_id):
    for student in students:
        if student["student_id"] == student_id:
            return student

    return None


def clear_students():
    students.clear()
