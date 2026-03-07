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

# ===============================
# ADMIN DASHBOARD (OVERVIEW ONLY)
# ===============================
@login_required
def admin_dashboard(request):
    """
    Admin can:
    - View total RECRUITER
    - View pending RECRUITER invites
    - View total jobs read
    - View total applications
    - View application status breakdown
    """

    if request.user.role not in ["ADMIN", "SUPERUSER"]:
        raise PermissionDenied() #   "403 Forbidden"

    # ---------------- RECRUITER USERS ----------------
    recruiter_users_qs = User.objects.filter(role="RECRUITER").order_by("-created_at")   #  sort by creation date,   
    recruiter_paginator = Paginator(recruiter_users_qs, 10) # Split the RECRUITER users into pages of 10.
    recruiter_page = recruiter_paginator.get_page(request.GET.get("recruiter_page")) #  Which page is the user asking for? Like ?
    # request.GET.get("recruiter_page") looks for a URL parameter like ?recruiter_page=2
    
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
        "recruiter_page": recruiter_page,
        "pending_invites_page": pending_invites_page,
        "total_jobs": total_jobs,
        "total_applications": total_applications,
        "status_counts": status_counts,
    },
    )

# ========================
# RECRUITER MANAGEMENT (LIST RECRUITER USERS)
# ========================
@login_required
def recruiter_management(request):
    """
    Admin can:
    - View RECRUITER users
    - Search RECRUITER users
    """

    if request.user.role not in ["ADMIN", "SUPERUSER"]:
        raise PermissionDenied()

    search = request.GET.get("search", "").strip() # Get search keyword from URL and .strip() removes extra spaces

    recruiter_users = User.objects.filter(role="RECRUITER").order_by("-created_at")

    if search:
        recruiter_users = recruiter_users.filter(email__icontains=search) # If user searches, filter by email

    paginator = Paginator(recruiter_users, 10)   
    recruiter_page = paginator.get_page(request.GET.get("page")) # If user searches, filter by email

    return render(      
    request,
    "admin/recruiter_management.html",
    {
        "recruiter_page": recruiter_page,
        "search": search,
        
    },
    )


# ==========================
# ACTIVATE / SUSPEND RECRUITER ajax
# ===========================
@login_required
@require_POST
def suspend_recruiter(request, user_id):
    """
    Disable RECRUITER account
    """

    if request.user.role not in ["ADMIN", "SUPERUSER"]:
        raise PermissionDenied()

    recruiter = get_object_or_404(User, id=user_id, role="RECRUITER")
    recruiter.is_active = False
    recruiter.save() # Disable RECRUITER account

    logger.info(
        f"RECRUITER suspended: {recruiter.email} by {request.user.email}" 
    )

    return JsonResponse({"status": "suspended"}) # Send JSON response to frontend and This is sent back to JavaScript


@login_required
@require_POST
def activate_recruiter(request, user_id):
    """
    Enable RECRUITER account
    """

    if request.user.role not in ["ADMIN", "SUPERUSER"]:
        raise PermissionDenied()

    recruiter = get_object_or_404(User, id=user_id, role="RECRUITER")
    recruiter.is_active = True 
    recruiter.save()

    logger.info(
        f"RECRUITER activated: {recruiter.email} by {request.user.email}"
    )

    return JsonResponse({"status": "activated"})


# ===========
# INVITE RECRUITER
# ===========
@login_required
def invite_page(request):
    """
    Admin invites RECRUITER via email
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
            subject="HireFlow RECRUITER Invitation",
            html_content=f"""
                <p>Hello,</p>
                <p>You have been invited to join <strong>HireFlow</strong> as a RECRUITER user.</p>
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
    "recruiter/invite.html",
    
    {
        "hide_sidebar": True,   # ✅ ADD THIS
    },
)


# =====================================================
# ADMIN – view all job and read only 
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
            
        },
    )


# ===========================
# ADMIN – JOB DETAIL read only 
# =============================
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
            
        }
    )