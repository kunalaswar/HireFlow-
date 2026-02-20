from django.shortcuts import render, redirect, get_object_or_404
from applications.forms import ApplicationForm
from jobs.models import Job
from applications.models import Application
from applications.supabase_client import upload_resume
import logging
from core.utils.email import send_brevo_email

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
                try:
                    track_url = request.build_absolute_uri(
                    f"/applications/track/{application.application_id}/"
                    )

                    send_brevo_email(
                    to_email=application.email,
                    subject="Application Received – HireFlow",
                    html_content=f"""
                    <p>Hi {application.full_name},</p>

                    <p>Your application for 
                    <strong>{job.title}</strong> has been received.</p>

                    <p><strong>Application ID:</strong> {application.application_id}</p>

                    <p>
                    You can track your application status here:
                    <br>
                    <a href="{track_url}">
                        Track Application
                    </a>
                    </p>

                    <p>Thank you,<br>HireFlow Team</p>
                    """,
                    )
                except Exception as email_error:
                    logger.exception(email_error)
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

from django.http import Http404

def track_application(request, application_id):
    try:
        application = Application.objects.select_related("job").get(
            application_id=application_id
        )
    except Application.DoesNotExist:
        raise Http404("Application not found")

    return render(
        request,
        "applications/track.html",
        {
            "application": application,
            "hide_sidebar": True,
        },
    )