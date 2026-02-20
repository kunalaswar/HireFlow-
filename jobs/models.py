# jobs/models.py

from django.db import models
from django.conf import settings
from django.utils.text import slugify # converts job title into URL-friendly text
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal


class Job(models.Model):

    EMPLOYMENT_TYPES = [
        ("full_time", "Full Time"), # First part ("full_time") = saved in database 
        ("part_time", "Part Time"), # Second part ("Full Time") = shown to user 
        ("contract", "Contract"),
        ("internship", "Internship"),
    ]

    WORK_MODES = [
        ("onsite", "On-site"),
        ("remote", "Remote"),
        ("hybrid", "Hybrid"),
    ]

    SALARY_TYPES = [
        ("yearly", "Yearly (LPA)"),
        ("monthly", "Monthly (INR)"),
        ("negotiable", "Negotiable"),
        ("not_disclosed", "Not Disclosed"),
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    description = models.TextField()

    min_experience = models.FloatField(null=True, blank=True)
    max_experience = models.FloatField(null=True, blank=True)

    salary_type = models.CharField(
        max_length=20, choices=SALARY_TYPES, default="yearly"
    )
    min_salary = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    max_salary = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )

    location = models.CharField(max_length=255)
    work_mode = models.CharField(max_length=20, choices=WORK_MODES)
    employment_type = models.CharField(
        max_length=20, choices=EMPLOYMENT_TYPES, default="full_time"
    )

    required_education = models.CharField(
        max_length=255, blank=True, null=True
    )

    vacancies = models.PositiveIntegerField(default=1)
    deadline = models.DateField(null=True, blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="jobs"
    ) # Links job to HR user If HR is deleted → job stays (SET_NULL)
#     Who created this job? Links to the HR user who posted it.
# ForeignKey = creates a relationship. One user can create many jobs. One job belongs to one user.
# settings.AUTH_USER_MODEL = points to our User model (from users/models.py)
# on_delete=models.SET_NULL = if the HR user is deleted, don't delete the job — just set created_by to NULL (empty). The job stays.
# null=True = can be empty
# related_name="jobs" = reverse lookup. From a user, you can access user.jobs.all() to get all jobs they created.


    created_at = models.DateTimeField(auto_now_add=True) # when job was created
    is_deleted = models.BooleanField(default=False) # is_deleted → soft delete  Job is hidden   Not removed from DB
    #The job doesn't show on the website But the data still exists (for records, reports, backups) Can be restored later if needed
    def save(self, *args, **kwargs): # This runs every time you save a job.override it to add our own logic.    
        if not self.slug: # Automatically creates a unique URL slug 
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Job.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs) # No manual slug handling needed

    def clean(self):
        if self.min_experience and self.max_experience:
            if self.min_experience > self.max_experience:
                raise ValidationError("Min experience cannot exceed max experience.")

        if self.min_salary and self.max_salary:
            if self.min_salary > self.max_salary:
                raise ValidationError("Min salary cannot exceed max salary.")

    def __str__(self):
        return self.title
