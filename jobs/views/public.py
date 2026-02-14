# jobs/views/public.py

from django.views.generic import ListView, DetailView
from django.db.models import Q, Min, Max
from jobs.models import Job


# =====================================================
# Public Job List (Candidate Side)
# =====================================================

class PublicJobListView(ListView):
    model = Job
    template_name = "jobs/public_jobs_list.html"
    context_object_name = "jobs"
    paginate_by = 10

    def get_queryset(self):
        qs = Job.objects.filter(is_deleted=False)

        search = self.request.GET.get("search")
        location = self.request.GET.get("location")
        work_mode = self.request.GET.get("work_mode")
        job_type = self.request.GET.get("job_type")
        min_salary = self.request.GET.get("min_salary")
        max_salary = self.request.GET.get("max_salary")
        sort = self.request.GET.get("sort")

        # ----------------------------
        # Search
        # ----------------------------
        if search:
            qs = qs.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )

        # ----------------------------
        # Filters
        # ----------------------------
        if location:
            qs = qs.filter(location__icontains=location)

        if work_mode:
            qs = qs.filter(work_mode=work_mode)

        if job_type:
            qs = qs.filter(employment_type=job_type)

        # ----------------------------
        # Salary range filtering (EXACT)
        # ----------------------------
        if min_salary:
            qs = qs.filter(
                min_salary__isnull=False,
                min_salary__gte=min_salary
            )

        if max_salary:
            qs = qs.filter(
                max_salary__isnull=False,
                max_salary__lte=max_salary
            )

        # ---------------------------
        # Sorting
        # ----------------------------
        if sort == "salary_low":
            qs = qs.order_by("min_salary")
        elif sort == "salary_high":
            qs = qs.order_by("-max_salary")
        else:
            qs = qs.order_by("-created_at")

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #  hide sidebar & logout on public page
        context["hide_sidebar"] = True


        # ----------------------------
        # Global salary range (EXACT)
        # ----------------------------
        salary_range = Job.objects.filter(
            is_deleted=False
        ).aggregate(
            min_salary_global=Min("min_salary"),
            max_salary_global=Max("max_salary")
        )

        context["salary_min_global"] = salary_range["min_salary_global"] or 0
        context["salary_max_global"] = (
            salary_range["max_salary_global"] or 1000000
        )

        return context

# =====================================================
# Public Job Detail
# =====================================================

class PublicJobDetailView(DetailView):
    model = Job
    template_name = "jobs/public_job_detail.html"
    context_object_name = "job"
    slug_field = "slug"
    slug_url_kwarg = "slug" # Instead of using ID, use SLUG to find job.
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # hide sidebar & logout on public page
        context["hide_sidebar"] = True

        return context       
    
# ✔ Fetches job using slug
# ✔ Sends job to template
# ✔ Shows full job information
# ✔ Shows Apply button    