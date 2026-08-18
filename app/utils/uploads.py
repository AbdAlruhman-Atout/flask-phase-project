from pathlib import Path
from uuid import uuid4

from flask import current_app
from werkzeug.utils import secure_filename


def save_profile_picture(file_storage):
    original_name = secure_filename(file_storage.filename)

    extension = Path(original_name).suffix.lower()

    filename = f"{uuid4().hex}{extension}"

    upload_folder = Path(current_app.config["PROFILE_UPLOAD_FOLDER"])

    upload_folder.mkdir(
        parents=True,
        exist_ok=True,
    )

    file_storage.save(upload_folder / filename)

    return f"uploads/profiles/{filename}"


def delete_profile_picture(relative_path):
    if not relative_path:
        return

    file_path = Path(current_app.static_folder) / relative_path

    if file_path.is_file():
        file_path.unlink()
