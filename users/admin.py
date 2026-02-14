from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin  # Django already has a pre-made admin layout for users called UserAdmin. But we import it with a new name BaseUserAdmin — because WE are going to make our own UserAdmin on top of it.
# Why rename? Because if we don't rename, our own class name will clash with Django's class name. Same name = confusion. So we call Django's version BaseUserAdmin.
from users.models import (
    User,
    Invite,
    PasswordReset,
    EmailVerificationToken
)

# --------------------------
# Custom User Admin
# --------------------------
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ("email",)
    list_display = ("email", "role", "is_active", "is_staff", "is_superuser")
    search_fields = ("email",)
    list_filter = ("role", "is_active")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name")}),
        ("Role & Status", {"fields": ("role", "is_active", "must_change_password")}),
        ("Permissions", {"fields": ("is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "role"),
        }),
    )

    USERNAME_FIELD = "email"
    filter_horizontal = ("groups", "user_permissions")


# --------------------------
# Invite Admin
# --------------------------
@admin.register(Invite)
class InviteAdmin(admin.ModelAdmin):
    list_display = ("email", "created_by_email", "used", "expires_at")
    search_fields = ("email",)
    list_filter = ("used",)


# --------------------------
# Password Reset Admin
# --------------------------
@admin.register(PasswordReset)
class PasswordResetAdmin(admin.ModelAdmin):
    list_display = ("user", "used", "expires_at", "created_at")
    list_filter = ("used",)


# --------------------------
# Email Verification Admin
# --------------------------
@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "is_used", "created_at")
    list_filter = ("is_used",)

