# jobs/forms.py

from django import forms
from decimal import Decimal
from jobs.models import Job


class JobForm(forms.ModelForm):

    min_salary = forms.DecimalField(
        required=False,
        max_digits=12,
        decimal_places=2,
        help_text="Enter salary in LPA (for yearly)"
    )
    max_salary = forms.DecimalField(
        required=False,
        max_digits=12,
        decimal_places=2,
        help_text="Enter salary in LPA (for yearly)"
    )

    class Meta:
        model = Job
        exclude = [
            "created_by",
            "slug",
            "is_deleted",
            "created_at",
        ]
        widgets = {
            "deadline": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["min_salary"].widget.attrs.update({"step": "0.01"})
        self.fields["max_salary"].widget.attrs.update({"step": "0.01"})

        # Edit mode → show LPA instead of INR
        if self.instance.pk and self.instance.salary_type == "yearly":
            if self.instance.min_salary:
                self.initial["min_salary"] = (
                    Decimal(self.instance.min_salary) / Decimal("100000")
                ).quantize(Decimal("0.01"))

            if self.instance.max_salary:
                self.initial["max_salary"] = (
                    Decimal(self.instance.max_salary) / Decimal("100000")
                ).quantize(Decimal("0.01"))

    def save(self, commit=True):
        job = super().save(commit=False)

        # Preserve old values on edit
        if self.instance.pk:
            if self.cleaned_data.get("min_salary") in ["", None]:
                job.min_salary = self.instance.min_salary
            if self.cleaned_data.get("max_salary") in ["", None]:
                job.max_salary = self.instance.max_salary

        # Convert LPA → INR
        if job.salary_type == "yearly":
            if job.min_salary and job.min_salary < 1000:
                job.min_salary = (
                    Decimal(job.min_salary) * Decimal("100000")
                ).quantize(Decimal("0.01"))

            if job.max_salary and job.max_salary < 1000:
                job.max_salary = (
                    Decimal(job.max_salary) * Decimal("100000")
                ).quantize(Decimal("0.01"))

        if commit:
            job.save()

        return job

    def clean(self):
        cleaned = super().clean()

        salary_type = cleaned.get("salary_type")
        min_salary = cleaned.get("min_salary")
        max_salary = cleaned.get("max_salary")

        if salary_type == "yearly":
            for val in [min_salary, max_salary]:
                if val is not None and val > Decimal("100"):
                    raise forms.ValidationError(
                        "Yearly salary must be entered in LPA (0–100)."
                    )

        return cleaned
