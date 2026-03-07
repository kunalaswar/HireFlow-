from django.shortcuts import render, get_object_or_404,redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from jobs.models import Job
from applications.models import Application
import logging

logger = logging.getLogger(__name__)


# ===============================================================
#                         RECRUITER DASHBOARD
# ===============================================================
@login_required
def recruiter_dashboard(request):

    if request.user.role != "RECRUITER":
        logger.warning(
            f"Unauthorized RECRUITER dashboard access attempt by {request.user.email}"
        )
        raise PermissionDenied()

    jobs = Job.objects.filter(
        created_by=request.user,
        is_deleted=False
    )

    applications = Application.objects.filter(
        job__created_by=request.user, # job__created_by → Django ORM relationship lookup.
        job__is_deleted=False
    )

    context = {
        "total_jobs": jobs.count(),
        "total_applications": applications.count(),
        "screening": applications.filter(status="screening").count(),
        "review": applications.filter(status="review").count(),
        "interview": applications.filter(status="interview").count(),
        "hired": applications.filter(status="hired").count(),
        "rejected": applications.filter(status="rejected").count(),

        
    }

    return render(request, "recruiter/recruiter_dashboard.html", context)


# # ===============================================================
# #                 RECRUITER JOB APPLICATIONS (JOB-WISE)
# # ===============================================================
# @login_required
# def recruiter_job_applications(request, id):
#     """
#     Shows ALL candidates who applied for ONE specific job
#     posted by the logged-in RECRUITER.
#     """

#     if request.user.role != "RECRUITER":
#         logger.warning(
#             f"Unauthorized RECRUITER applications access attempt by {request.user.email}"
#         )
#         raise PermissionDenied()

#     # Get the job posted by this RECRUITER
#     job = get_object_or_404(
#         Job,
#         id=id,
#         created_by=request.user,
#         is_deleted=False
#     )

#     # Get applications ONLY for this job
#     applications = Application.objects.filter(
#         job=job
#     ).order_by("-applied_at")

#     return render(
#         request,
#         "recruiter/applications/job_applications.html",
#         {
#             "job": job,
#             "applications": applications
#         }
#     )

# ===============================================================
#        RECRUITER – UPDATE APPLICATION STATUS (INLINE SAVE)
# ===============================================================
# @login_required #! recruiter_update_application_status
# def recruiter_job_applications(request, app_id):

#     if request.user.role != "RECRUITER":
#         raise PermissionDenied()

#     application = get_object_or_404(
#         Application,
#         id=app_id,
#         job__created_by=request.user
#     )

#     if request.method == "POST":
#         new_status = request.POST.get("status")

#         if new_status in dict(Application.STATUS_CHOICES):
#             application.status = new_status
#             application.save()

#     # 🔁 Redirect back to SAME applications page
#     return redirect(
#         "job_application.html",
#         id=application.job.id
#     )

# ===============================================================
#                 RECRUITER JOB APPLICATIONS PAGE
# ===============================================================
@login_required
def recruiter_job_applications(request, id):

    if request.user.role != "RECRUITER":
        logger.warning(
            f"Unauthorized RECRUITER applications access attempt by {request.user.email}"
        )
        raise PermissionDenied()

    job = get_object_or_404( Job,id=id, created_by=request.user, is_deleted=False )

    applications = Application.objects.filter(
        job=job
    ).order_by("-applied_at")

    return render(
        request,
        "recruiter/applications/job_applications.html",
        {
            "job": job,
            "applications": applications,
            "hide_sidebar": True,

        }
    )