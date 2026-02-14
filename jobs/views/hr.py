# jobs/views/hr.py

from django.views.generic import ListView, CreateView, UpdateView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.db.models import Count
import logging

from jobs.models import Job
from jobs.forms import JobForm

logger = logging.getLogger(__name__)


# =====================================================
# Shared queryset logic
# ADMIN -> sees all jobs (read-only)
# HR     -> sees only jobs created by them
# =====================================================
 #  Data-level permission filtering
def job_queryset_for(user):
    if user.role == "ADMIN":
        return Job.objects.filter(is_deleted=False) # Admin can see ALL jobs.
    return Job.objects.filter(created_by=user, is_deleted=False)


# =====================================================
# HR / ADMIN – Job List (My Jobs)
# =====================================================

class HRJobListView(LoginRequiredMixin, ListView):
    template_name = "hr/jobs/list.html"
    context_object_name = "jobs" 
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        if request.user.role not in ["HR", "ADMIN"]:
            logger.warning(
                f"Unauthorized job list access attempt by {request.user.email}"
            )
            return redirect("login")
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        qs = job_queryset_for(self.request.user).annotate(
            applications_count=Count("applications")   
        ).order_by("-created_at")     

        search = self.request.GET.get("search")
        location = self.request.GET.get("location")
        work_mode = self.request.GET.get("work_mode")

        if search:
            qs = qs.filter(title__icontains=search)
        if location:
            qs = qs.filter(location__icontains=location)
        if work_mode:
            qs = qs.filter(work_mode=work_mode)

        return qs
      #  this is only for hide the side bar 
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["hide_sidebar"] = True
        return context

# =====================================================
# HR – Create Job
# =====================================================

class HRJobCreateView(LoginRequiredMixin, CreateView):
    form_class = JobForm
    template_name = "hr/jobs/create.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != "HR":
            logger.warning(
                f"Unauthorized job creation attempt by {request.user.email}"
            )
            return HttpResponseForbidden("Only HR users can create jobs.")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        job = form.save(commit=False)
        job.created_by = self.request.user
        job.save()

        logger.info(f"Job created: id={job.id} by {self.request.user.email}")
        messages.success(self.request, "Job created successfully!")

        return redirect("hr_job_list")
    # this is for hide the sidebar 
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["hide_sidebar"] = True
        return context
    
# =====================================================
# HR / ADMIN – Job Detail (Read-only for Admin)
# =====================================================

class HRJobDetailView(LoginRequiredMixin, DetailView): # DetailView → Django built-in view for showing ONE object
    template_name = "hr/jobs/detail.html"
    context_object_name = "job"
    pk_url_kwarg = "id"

    def dispatch(self, request, *args, **kwargs):
        if request.user.role not in ["HR", "ADMIN"]:
            logger.warning(
                f"Unauthorized job detail access attempt by {request.user.email}"
            )
            return redirect("login")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return job_queryset_for(self.request.user)
    
      # this is for hide the sidebar 
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["hide_sidebar"] = True
        return context


# =====================================================
# HR – Update Job
# =====================================================
 
class HRJobUpdateView(LoginRequiredMixin, UpdateView): # UpdateView → Django built-in class for editing existing object
    model = Job
    form_class = JobForm
    template_name = "hr/jobs/edit.html"
    pk_url_kwarg = "id"

    def dispatch(self, request, *args, **kwargs):
        job = get_object_or_404(Job, id=kwargs["id"])

        if request.user.role == "ADMIN":
            logger.warning(f"Admin attempted to edit job {job.id}")
            return HttpResponseForbidden(
                "Admins are not allowed to edit jobs."
            )

        if job.created_by != request.user:
            logger.warning(
                f"Unauthorized job edit attempt by {request.user.email} on job {job.id}"
            )
            return HttpResponseForbidden("You are not allowed to edit this job.")

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        job = form.save()

        logger.info(f"Job updated: id={job.id} by {self.request.user.email}")
        messages.success(self.request, "Job updated successfully!")

        action = self.request.POST.get("action")     # 

        if action == "save_detail":
            return redirect("hr_job_detail", id=job.id)

        return redirect("hr_job_list")   
    
      # this is for hide the sidebar 
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["hide_sidebar"] = True
        return context

# =====================================================
# HR – Delete Job (Soft Delete)
# =====================================================

class HRJobDeleteView(LoginRequiredMixin, View):
    def post(self, request, id):
        job = get_object_or_404(Job, id=id) 

        if request.user.role != "HR" or job.created_by != request.user:
            logger.warning(
                f"Unauthorized job delete attempt by {request.user.email} on job {job.id}"
            )
            return HttpResponseForbidden("You cannot delete this job.")

        job.is_deleted = True   
        job.save()

        logger.info(f"Job soft-deleted: id={job.id} by {request.user.email}")
        messages.success(request, "Job deleted successfully!")

        return redirect("hr_job_list") 
    
      # this is for hide the sidebar 
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["hide_sidebar"] = True
        return context
