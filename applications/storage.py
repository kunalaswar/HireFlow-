import uuid
from django.conf import settings
from django.core.files.storage import default_storage


def upload_resume(file, job_slug):
    filename = f"resumes/{job_slug}/{uuid.uuid4()}_{file.name}"
    path = default_storage.save(filename, file)
    return default_storage.url(path)
