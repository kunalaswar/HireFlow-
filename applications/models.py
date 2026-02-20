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

    # ✅ NEW FIELD (DO NOT REMOVE)
    application_id = models.CharField(
    max_length=20,
    blank=True,
    null=True
)
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)

    resume_url = models.URLField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="screening"
    )

    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("job", "email")

    # ✅ NEW SAVE METHOD (AUTO GENERATE ID)
    def save(self, *args, **kwargs):
        if not self.application_id:
            last_application = Application.objects.exclude(
            application_id__isnull=True
            ).order_by("-id").first()

            if last_application and last_application.application_id:
                last_id = int(last_application.application_id.split("-")[1])
                new_id = last_id + 1
            else:
                new_id = 1

            self.application_id = f"HF-{str(new_id).zfill(4)}"

        super().save(*args, **kwargs)