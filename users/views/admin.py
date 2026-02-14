from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.http import JsonResponse
import uuid
import logging

from users.models import User, Invite
from jobs.models import Job
from applications.models import Application
from core.utils.email import send_brevo_email

logger = logging.getLogger(__name__)

# =====================================================
# ADMIN DASHBOARD (OVERVIEW ONLY)
# =====================================================
@login_required
def admin_dashboard(request):
    """
    Admin can:
    - View total HR
    - View pending HR invites
    - View total jobs read
    - View total applications
    - View application status breakdown
    """

    if request.user.role not in ["ADMIN", "SUPERUSER"]:
        raise PermissionDenied() #   "403 Forbidden"

    # ---------------- HR USERS ----------------
    hr_users_qs = User.objects.filter(role="HR").order_by("-created_at")   #  sort by creation date,   
    hr_paginator = Paginator(hr_users_qs, 10) # Split the HR users into pages of 10.
    hr_page = hr_paginator.get_page(request.GET.get("hr_page")) #  Which page is the user asking for? Like ?
    # request.GET.get("hr_page") looks for a URL parameter like ?hr_page=2
    
    # ---------------- PENDING INVITES ----------------
    pending_invites_qs = Invite.objects.filter(
        used=False,
        expires_at__gt=timezone.now()  # Get invites that: Are not used Are not expired -
    ).order_by("-created_at")

    pending_paginator = Paginator(pending_invites_qs, 10)
    pending_invites_page = pending_paginator.get_page(
        request.GET.get("pending_page")
    )

    # ---------------- JOB STATS ----------------
    total_jobs = Job.objects.filter(is_deleted=False).count()

    # ---------------- APPLICATION STATS ----------------
    applications_qs = Application.objects.filter(
        job__is_deleted=False
    )

    total_applications = applications_qs.count()

    status_counts = {
        "screening": applications_qs.filter(status="screening").count(),
        "review": applications_qs.filter(status="review").count(),
        "interview": applications_qs.filter(status="interview").count(),
        "hired": applications_qs.filter(status="hired").count(),
        "rejected": applications_qs.filter(status="rejected").count(),
    }

    return render(
    request,
    "admin/admin_dashboard.html",
    {
        "hr_page": hr_page,
        "pending_invites_page": pending_invites_page,
        "total_jobs": total_jobs,
        "total_applications": total_applications,
        "status_counts": status_counts,
        "hide_sidebar": True,   # ✅ THIS IS THE FIX 
    },
    )

# =====================================================
# HR MANAGEMENT (LIST HR USERS)
# =====================================================
@login_required
def hr_management(request):
    """
    Admin can:
    - View HR users
    - Search HR users
    """

    if request.user.role not in ["ADMIN", "SUPERUSER"]:
        raise PermissionDenied()

    search = request.GET.get("search", "").strip() # Get search keyword from URL and .strip() removes extra spaces

    hr_users = User.objects.filter(role="HR").order_by("-created_at")

    if search:
        hr_users = hr_users.filter(email__icontains=search) # If user searches, filter by email

    paginator = Paginator(hr_users, 10)   
    hr_page = paginator.get_page(request.GET.get("page")) # If user searches, filter by email

    return render(      
    request,
    "admin/hr_management.html",
    {
        "hr_page": hr_page,
        "search": search,
        "hide_sidebar": True,   # ✅ ADD THIS
    },
    )


# =====================================================
# ACTIVATE / SUSPEND HR (AJAX)
# =====================================================
@login_required
@require_POST
def suspend_hr(request, user_id):
    """
    Disable HR account
    """

    if request.user.role not in ["ADMIN", "SUPERUSER"]:
        raise PermissionDenied()

    hr = get_object_or_404(User, id=user_id, role="HR")
    hr.is_active = False
    hr.save() # Disable HR account

    logger.info(
        f"HR suspended: {hr.email} by {request.user.email}" 
    )

    return JsonResponse({"status": "suspended"}) # Send JSON response to frontend and This is sent back to JavaScript


@login_required
@require_POST
def activate_hr(request, user_id):
    """
    Enable HR account
    """

    if request.user.role not in ["ADMIN", "SUPERUSER"]:
        raise PermissionDenied()

    hr = get_object_or_404(User, id=user_id, role="HR")
    hr.is_active = True 
    hr.save()

    logger.info(
        f"HR activated: {hr.email} by {request.user.email}"
    )

    return JsonResponse({"status": "activated"})


# =====================================================
# INVITE HR
# =====================================================
@login_required
def invite_page(request):
    """
    Admin invites HR via email
    """   

    if request.user.role not in ["ADMIN", "SUPERUSER"]:
        raise PermissionDenied()

    if request.method == "POST":
        email = request.POST.get("email", "").strip()

        if not email:
            messages.error(request, "Email is required.")
            return redirect("invite")

        # Prevent duplicate active invite
        if Invite.objects.filter(
            email=email,
            used=False,
            expires_at__gt=timezone.now()
        ).exists():
            messages.warning(
                request,
                f"Invite already sent to {email}"
            )
            return redirect("invite")

        token = uuid.uuid4() # Generate unique invite token
        signup_link = request.build_absolute_uri(
            f"/signup/?token={token}"  # generated token passed here  
        )

        email_sent = send_brevo_email(
            to_email=email,
            subject="HireFlow HR Invitation",
            html_content=f"""
                <p>Hello,</p>
                <p>You have been invited to join <strong>HireFlow</strong> as an HR user.</p>
                <p>
                    <a href="{signup_link}">
                        Click here to create your account
                    </a>
                </p>
                <p>This link is valid for 48 hours.</p>
            """,
        )

        if not email_sent: 
            messages.error(
                request, "Failed to send email. Try again later."
            )
            return redirect("invite")

        Invite.objects.create(
            email=email,
            token=token,
            created_by=request.user,   
            created_by_email=request.user.email,
            expires_at=timezone.now() + timedelta(hours=48),
        )

        messages.success(
            request, f"Invite sent successfully to {email}"
        )

        return redirect("invite")

    return render(
    request,
    "hr/invite.html",
    {
        "hide_sidebar": True,   # ✅ ADD THIS
    },
)


# =====================================================
# ADMIN – VIEW ALL JOBS (READ ONLY)
# =====================================================
@login_required
def admin_job_list(request):
    """
    Admin can:
    - View all jobs (read-only)
    - Search jobs by title
    """

    if request.user.role not in ["ADMIN", "SUPERUSER"]:
        raise PermissionDenied()

    search = request.GET.get("search", "").strip()

    jobs_qs = Job.objects.filter(is_deleted=False).order_by("-created_at") # Only active jobs

    if search:
        jobs_qs = jobs_qs.filter(title__icontains=search) # Search jobs by title

    paginator = Paginator(jobs_qs, 10)
    jobs_page = paginator.get_page(request.GET.get("page"))

    return render(   
        request,
        "admin/jobs_list.html",
        {
            "jobs_page": jobs_page,
            "search": search,
            "hide_sidebar": True,   #
        },
    )


# =====================================================
# ADMIN – JOB DETAIL (READ ONLY)
# =====================================================
@login_required
def admin_job_detail(request, id):
    """
    Admin can:
    - View job details
    - Cannot edit/delete
    """

    if request.user.role not in ["ADMIN", "SUPERUSER"]:
        raise PermissionDenied()

    job = get_object_or_404(Job, id=id, is_deleted=False) # Fetch job or show 404

    return render(
        request,
        "admin/job_detail.html",
        {
            "job": job,
            "hide_sidebar": True,   # 
        }
    )
