from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.conf import settings
import uuid # This creates a unique random number (like a secret key). Example: a1b2c3d4-.... We use this for invite tokens and reset tokens.


# --------------------------
# Custom User Manager
# --------------------------
class UserManager(BaseUserManager):   # AbstractUser = A ready-made user template. It already has fields like first_name, last_name, password, is_active. 
    use_in_migrations = True  

    def create_user(self, email, password=None, **extra_fields): # This method creates a normal user. email is required.

        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email) # What is normalize? It makes the email clean. Example: Hello@Gmail.COM becomes Hello@gmail.com. The domain part becomes lowercase. This is a pre-defined method from BaseUserManager.
        user = self.model(email=email, **extra_fields)  
        user.set_password(password)
        user.save(using=self._db) 
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "SUPERUSER")
        extra_fields.setdefault("must_change_password", False)
        extra_fields.setdefault("is_active", True)

        return self.create_user(email, password, **extra_fields)
# User Signs Up
#     ↓
# EmailVerificationToken created (is_used = False)
#     ↓
# User clicks verify link in email
#     ↓
# is_used = True, User.is_active = True
#     ↓
# User can now LOGIN


# --------------------------
# Custom User Model
# --------------------------   
class User(AbstractUser): # AbstractUser → Django built-in base user model.
    username = None
    USERNAME_FIELD = "email" 
    REQUIRED_FIELDS = []

    ROLE_CHOICES = [
        ("SUPERUSER", "SuperUser"),
        ("ADMIN", "Admin"),
        ("HR", "HR Recruiter"),
    ]

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="HR")

    # IMPORTANT: inactive until email verified
    is_active = models.BooleanField(default=False)

    must_change_password = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)   
    updated_at = models.DateTimeField(auto_now=True) # 

    objects = UserManager() 
 
    def __str__(self): # Used for: Django admin display
        return f"{self.email} - {self.role}"


# --------------------------
# Invite Model 
# --------------------------
class Invite(models.Model):
    email = models.EmailField() # The email of the person being invited.
    token = models.UUIDField(default=uuid.uuid4, unique=True) # A unique secret code (like a1b2c3d4-e5f6-...). This is used in the invite link. Only the person with this token can accept the invite.

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,   
        on_delete=models.SET_NULL
    )
    created_by_email = models.CharField(max_length=255, null=True, blank=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self): # This checks: Is current time greater than expiry time
        return timezone.now() > self.expires_at

    def __str__(self): 
        return f"Invite to {self.email}" 
# Admin invites HR
#     ↓
# Invite created (used = False, has expiry)
#     ↓
# Person clicks invite link
#     ↓
# New User created (must_change_password = True)
#     ↓
# Person sets new password → can LOGIN

# --------------------------
# Password Reset
# --------------------------
class PasswordReset(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    ) # Links to the user who wants to reset password. CASCADE means if the user is deleted, the reset record is also deleted.
    token = models.UUIDField(default=uuid.uuid4, unique=True) # A unique secret code sent in the reset email link.
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)
    consumed_at = models.DateTimeField(null=True, blank=True)
    request_ip = models.CharField(max_length=50, null=True, blank=True)
    user_agent = models.CharField(max_length=255, null=True, blank=True)

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"Reset token for {self.user.email}"

# User forgets password
#     ↓
# PasswordReset token created
#     ↓
# User clicks reset link in email
#     ↓
# Sets new password → used = True
# --------------------------
# Email Verification Token
# --------------------------
class EmailVerificationToken(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    ) # 
    token = models.UUIDField(default=uuid.uuid4, unique=True) # this is create unique token 
    created_at = models.DateTimeField(auto_now_add=True) 
    is_used = models.BooleanField(default=False)   

    def __str__(self):
        return f"Email verification for {self.user.email}"

