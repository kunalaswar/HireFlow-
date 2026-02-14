from django import forms
from applications.models import Application
from django.core.validators import FileExtensionValidator, validate_email
from django.core.exceptions import ValidationError
import re


class ApplicationForm(forms.ModelForm):
    """
    Candidate job application form.
    Used on Apply Job page.
    """

    resume = forms.FileField(
        validators=[FileExtensionValidator(allowed_extensions=["pdf"])],
        widget=forms.FileInput(attrs={"accept": ".pdf"})
    )

    class Meta:
        model = Application
        fields = ["full_name", "email", "phone", "resume"]

    # ----------------------------
    # FULL NAME VALIDATION
    # ----------------------------
    def clean_full_name(self):
        name = self.cleaned_data.get("full_name", "").strip()

        if len(name) < 3:
            raise ValidationError("Full name must be at least 3 characters.")

        # Only letters, spaces, dots allowed
        if not re.match(r"^[A-Za-z\s.]+$", name):
            raise ValidationError("Name can contain only letters and spaces.")

        return name

    # ----------------------------
    # EMAIL VALIDATION
    # ----------------------------
    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip()

        try:
            validate_email(email)
        except ValidationError:
            raise ValidationError("Enter a valid email address.")

        return email

    # ----------------------------
    # PHONE VALIDATION
    # ----------------------------
    def clean_phone(self):
        raw = self.cleaned_data.get("phone", "").strip()

        # Keep leading + if present
        if raw.startswith("+"):
            cleaned = "+" + re.sub(r"\D", "", raw[1:])
        else:
            cleaned = re.sub(r"\D", "", raw)

        digits_only = re.sub(r"\D", "", cleaned)

        if len(digits_only) < 7 or len(digits_only) > 15:
            raise ValidationError("Enter a valid phone number.")

        return cleaned

    # ----------------------------
    # RESUME VALIDATION
    # ----------------------------
    def clean_resume(self):
        resume = self.cleaned_data.get("resume")

        if not resume:
            raise ValidationError("Resume is required.")

        # Max size: 5MB
        if resume.size > 5 * 1024 * 1024:
            raise ValidationError("Resume size cannot exceed 5MB.")

        return resume
