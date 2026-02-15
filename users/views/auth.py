from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages # Shows pop-up messages to the user. Like "Registration successful!" or "Invalid password". These are shown on the next page after a redirect.
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from users.models import User, Invite, PasswordReset, EmailVerificationToken

from core.utils.email import send_brevo_email  # Brevo logic (API key goes in settings)

from datetime import timedelta
import uuid
import logging


logger = logging.getLogger(__name__)
# =====================================================
# REGISTER (SEND VERIFICATION EMAIL)
# =====================================================
# def register_page(request):
#     if request.method == "POST":
#         email = request.POST.get("email")
#         password = request.POST.get("password")
#         confirm_password = request.POST.get("confirm_password")

#         if password != confirm_password:
#             messages.error(request, "Passwords do not match")
#             return redirect("register")

#         try:
#             validate_password(password) 
#         except ValidationError as e:    
#             messages.error(request, " ".join(e.messages))
#             return redirect("register")

#         if User.objects.filter(email=email).exists(): #this email already used? .filter().exists() = "Search the database.
#             messages.error(request, "Email already registered")
#             return redirect("register")

#         # Create inactive user
#         user = User.objects.create_user(
#             email=email,
#             password=password,
#             role="HR",
#             is_active=True
#         )    

#         # Create verification token
#         token_obj = EmailVerificationToken.objects.create(user=user)

#         verify_link = request.build_absolute_uri(
#             f"/verify-email/?token={token_obj.token}"
#         )

#         send_brevo_email(
#             to_email=email,
#             subject="Verify your HireFlow account",
#             html_content=f"""
#                 <h3>Verify your email</h3>
#                 <p>Click the link below to verify your email:</p>
#                 <a href="{verify_link}">Verify Email</a>
#             """
#         )         

#         messages.success(
#             request,
#             "Registration successful! Please check your email to verify your account."
#         )
#         return redirect("login")

#     return render(request, "auth/signup.html")

def register_page(request):
    token = request.GET.get("token")

    invite = None

    # 🔹 If token exists → This is HR invite flow
    if token:
        try:
            invite = Invite.objects.get(
                token=token,
                used=False,
                expires_at__gt=timezone.now()
            )
        except Invite.DoesNotExist:
            messages.error(request, "Invalid or expired invite link.")
            return redirect("login")

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect(request.path)

        try:
            validate_password(password)
        except ValidationError as e:
            messages.error(request, " ".join(e.messages))
            return redirect(request.path)

        # 🔹 If Invite Flow
        if invite:
            user = User.objects.create_user(
                email=invite.email,
                password=password,
                role="HR",
                is_active=True   # 🔥 IMPORTANT FIX
            )

            invite.used = True
            invite.save()

            messages.success(request, "Account created successfully. Please login.")
            return redirect("login")

        # 🔹 Normal Public Register (optional)
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return redirect("register")

        user = User.objects.create_user(
            email=email,
            password=password,
            role="HR",
            is_active=True
        )

        messages.success(request, "Registration successful. Please login.")
        return redirect("login")

    return render(request, "auth/signup.html", {"invite": invite})


# =====================================================
# VERIFY EMAIL
# =====================================================
def verify_email(request):
    token = request.GET.get("token")

    try:
        token_obj = EmailVerificationToken.objects.get(
            token=token, # token must match
            is_used=False # is_used must be False
        )
    except EmailVerificationToken.DoesNotExist:
        messages.error(request, "Invalid or expired verification link")
        return redirect("login")   

    user = token_obj.user
    user.is_active = True
    user.save()

    token_obj.is_used = True
    token_obj.save()

    messages.success(request, "Email verified successfully. You can now log in.")
    return redirect("login") # Validates token → activates user → blocks token reuse.

# =====================================================
# LOGIN
# =====================================================
def login_page(request):
    """
    Email + password login 
    Rate limit enabled only in production
    """

    if settings.ENVIRONMENT == "production":
        from django_ratelimit.decorators import ratelimit

        @ratelimit(key="ip", rate="5/m", method="POST")
        def _wrapped(request):
            return _login_logic(request) 

        return _wrapped(request)

    return _login_logic(request)

def _login_logic(request):

    # If already logged in → redirect properly
    if request.user.is_authenticated:
        if request.user.role in ["ADMIN", "SUPERUSER"]:
            return redirect("admin_dashboard")
        if request.user.role == "HR":
            return redirect("hr_dashboard")
        return redirect("/")

    # Handle login POST
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user_obj = User.objects.get(email=email)
        except User.DoesNotExist:
            return render(request, "auth/login.html", {"error": "Invalid credentials"})

        # Check email verified
        if not user_obj.is_active:
            return render(
                request,
                "auth/login.html",
                {"error": "Please verify your email before login"},
            )

        user = authenticate(request, email=email, password=password)

        if not user:
            return render(request, "auth/login.html", {"error": "Invalid credentials"})

        login(request, user)

        if user.role in ["ADMIN", "SUPERUSER"]:
            return redirect("admin_dashboard")

        if user.role == "HR":
            return redirect("hr_dashboard")

        return redirect("/")

    return render(request, "auth/login.html")


# =====================================================
# LOGOUT
# =====================================================
def logout_user(request):
    logout(request) # logout → Django built-in function. It removes user session from server.
    return redirect("login")   

# =====================================================
# PROFILE (OPTIONAL)
# =====================================================
@login_required
def profile_view(request):
    if request.method == "POST":
        request.user.first_name = request.POST.get("first_name")
        request.user.last_name = request.POST.get("last_name")
        request.user.save()
        messages.success(request, "Profile updated")
        return redirect("profile")

    return render(request, "auth/profile.html")


# =====================================================
# FORGOT PASSWORD
# =====================================================
def forgot_password_request(request):
    if request.method == "POST":
        email = request.POST.get("email")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.success(request, "If the email exists, a reset link was sent.")
            return redirect("forgot_password")

        token = uuid.uuid4()
        reset_link = request.build_absolute_uri(f"/reset-password/?token={token}")

        # NOTE: Add your Brevo API key in settings.py
        send_brevo_email(
            to_email=email,
            subject="Reset your HireFlow password",
            html_content=f"""
                <p>Click below to reset your password:</p>
                <a href="{reset_link}">Reset Password</a>
            """,
        )

        PasswordReset.objects.create(
            user=user,
            token=token,
            expires_at=timezone.now() + timedelta(minutes=15),
        )   

        messages.success(request, "Password reset link sent.")
        return redirect("forgot_password")

    return render(request, "auth/forgot_password.html")


# =====================================================
# RESET PASSWORD
# =====================================================
def reset_password_page(request):
    token = request.GET.get("token") # Gets the token from the URL when user clicks the reset link.

    try:
        reset_obj = PasswordReset.objects.get(token=token, used=False)  # Finds this token in the database. Must exist AND must not be used already. If not found → show error.
    except PasswordReset.DoesNotExist:
        return render(request, "auth/reset_password.html", {"error": "Invalid token"})

    if reset_obj.is_expired():
        return render(request, "auth/reset_password.html", {"error": "Token expired"})

    if request.method == "POST":
        p1 = request.POST.get("password")
        p2 = request.POST.get("confirm_password")

        if p1 != p2:
            return render(request, "auth/reset_password.html", {"error": "Passwords do not match"})

        validate_password(p1)   
    
        user = reset_obj.user   
        user.set_password(p1)
        user.save()

        reset_obj.used = True
        reset_obj.save()

        messages.success(request, "Password changed successfully")
        return redirect("login")

    return render(request, "auth/reset_password.html", {"token": token})


