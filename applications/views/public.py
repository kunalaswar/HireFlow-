from django.shortcuts import render, redirect, get_object_or_404
from applications.forms import ApplicationForm
from jobs.models import Job
from applications.models import Application
from applications.supabase_client import upload_resume
import logging

logger = logging.getLogger(__name__)


def apply_job(request, slug):
    job = get_object_or_404(Job, slug=slug)

    if request.method == "POST":
        form = ApplicationForm(request.POST, request.FILES)

        if form.is_valid():
            email = form.cleaned_data["email"]

            # Duplicate check
            if Application.objects.filter(job=job, email=email).exists():
                form.add_error("email", "You have already applied for this job.")
                return render(
                    request,
                    "applications/apply.html",
                    {"form": form, "job": job, "hide_sidebar": True}
                )

            application = form.save(commit=False)
            application.job = job

            resume_file = request.FILES.get("resume")

            if not resume_file:
                form.add_error("resume", "Resume is required.")
                return render(
                    request,
                    "applications/apply.html",
                    {"form": form, "job": job, "hide_sidebar": True}
                )

            try:
                # Upload to Supabase
                resume_file.seek(0)
                public_url = upload_resume(resume_file, job.slug)

                # Save public URL in model
                application.resume_url = public_url

                application.save()

            except Exception as e:
                logger.exception(e)
                form.add_error("resume", "Resume upload failed. Please try again.")
                return render(
                    request,
                    "applications/apply.html",
                    {"form": form, "job": job, "hide_sidebar": True}
                )

            return redirect("application_success")

    else:
        form = ApplicationForm()

    return render(
        request,
        "applications/apply.html",
        {"form": form, "job": job, "hide_sidebar": True}
    )


def application_success(request):
    return render(
        request,
        "applications/success.html",
        {"hide_sidebar": True}
    )
