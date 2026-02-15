from supabase import create_client
import os
import uuid


BUCKET = os.getenv("SUPABASE_BUCKET", "resumes")


def get_supabase_client():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        raise Exception("Supabase credentials missing in environment variables")

    return create_client(url, key)


def upload_resume(file, job_slug):
    supabase = get_supabase_client()

    ext = file.name.split(".")[-1].lower()
    filename = f"{job_slug}/{uuid.uuid4()}.{ext}"

    file.seek(0)
    file_bytes = file.read()

    try:
        supabase.storage.from_(BUCKET).upload(
            path=filename,
            file=file_bytes,
            file_options={
                "content-type": "application/pdf",
                "x-upsert": "false",
            },
        )
    except Exception as e:
        raise Exception(f"Supabase upload failed: {e}")

    return supabase.storage.from_(BUCKET).get_public_url(filename)
