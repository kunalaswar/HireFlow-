from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, DetailView, UpdateView,View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from applications.models import Application
import logging
from django.http import JsonResponse

logger = logging.getLogger(__name__)

# ===============================================================
# QUERYSET HELPER (HR ONLY)
# ===============================================================
def app_queryset_for(user):   
    """
    Returns applications only for jobs created by this HR
    """
    return Application.objects.filter(
        job__created_by=user,
        job__is_deleted=False,
    )

# ===============================================================
# HR – ALL APPLICATIONS LIST
# ===============================================================
class HRApplicationListView(LoginRequiredMixin, ListView):
    template_name = "hr/applications/list.html"
    context_object_name = "apps_page"
    paginate_by = 10
    

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != "HR":
            # raise PermissionDenied()
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self): 
        qs = app_queryset_for(self.request.user).order_by("-applied_at")

        # Search by candidate name ONLY
        search = self.request.GET.get("search", "").strip()
        if search:
            qs = qs.filter(full_name__icontains=search)

        # Status filter
        status_filter = self.request.GET.get("status", "")
        if status_filter:
            qs = qs.filter(status=status_filter)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = self.get_queryset()

        # Status counts (for filter dropdown) #! this is we Extra added 
        context["counts"] = {
            "screening": qs.filter(status="screening").count(),
            "review": qs.filter(status="review").count(),
            "interview": qs.filter(status="interview").count(),
            "hired": qs.filter(status="hired").count(),
            "rejected": qs.filter(status="rejected").count(),
        }

        context["search"] = self.request.GET.get("search", "")
        context["status_filter"] = self.request.GET.get("status", "")
        

    
        return context


# ===============================================================
# HR – APPLICATION DETAIL PAGE
# ===============================================================
class HRApplicationDetailView(LoginRequiredMixin, DetailView):
    template_name = "hr/applications/detail.html"
    context_object_name = "app"

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != "HR":
            # raise PermissionDenied()
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):   
        return app_queryset_for(self.request.user)   

    
# ====================================
# HR – STATUS UPDATE PAGE 
# ====================================

from core.utils.email import send_brevo_email
from django.conf import settings

class HRStatusUpdateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        if request.user.role != "HR":
            return JsonResponse({"error": "Unauthorized"}, status=403)

        application = get_object_or_404(
            Application,
            pk=pk,
            job__created_by=request.user,
        )

        old_status = application.status
        new_status = request.POST.get("status")

        ALLOWED_STATUSES = {
            "screening",
            "review",
            "interview",
            "hired",
            "rejected",
        }

        if new_status not in ALLOWED_STATUSES:
            return JsonResponse({"error": "Invalid status"}, status=400)

        # Only update if status changed
        if old_status != new_status:
            application.status = new_status
            application.save(update_fields=["status"])

            try:
                track_url = request.build_absolute_uri(
                    f"/applications/track/{application.application_id}/"
                )

                send_brevo_email(
                    to_email=application.email,
                    subject="Application Status Updated – HireFlow",
                    html_content=f"""
                        <p>Hi {application.full_name},</p>

                        <p>Your application for 
                        <strong>{application.job.title}</strong> 
                        has been updated.</p>

                        <p><strong>New Status:</strong> {new_status.title()}</p>

                        <p>
                        You can track your application here:
                        <br>
                        <a href="{track_url}">Track Application</a>
                        </p>

                        <p>Regards,<br>HireFlow Team</p>
                    """,
                )
            except Exception:
                logger.exception("Status email failed")

        from django.contrib import messages

        messages.success(
        request,
        f"Application status updated successfully. Email sent to {application.email}."
)

    #    from django.shortcuts import redirect

        return redirect("hr_applications_list")


# ===============================================================
# HR – RESUME PREVIEW
# ===============================================================
@login_required
def preview_resume(request, pk):
    application = get_object_or_404(
        Application,
        pk=pk,
        job__created_by=request.user,
        job__is_deleted=False,
    )
    # return redirect(application.resume.url)
    return redirect(application.resume_url)  # this is a application model and resume_url is field 


# resume_url = models.URLField()
# That means:
# Instead of storing uploaded file locally,
# You are storing:
