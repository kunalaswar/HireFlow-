# applications/models.py

from django.db import models
from jobs.models import Job


STATUS_CHOICES = [
    ("screening", "Screening"),
    ("review", "Review"),
    ("interview", "Interview"),
    ("hired", "Hired"),
    ("rejected", "Rejected"),
]


class Application(models.Model):
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name="applications"
    )

    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)

    # ✅ Store Supabase public URL
    resume_url = models.URLField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="screening"
    )

    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("job", "email")

    def __str__(self):
        return f"{self.full_name} - {self.job.title}"
