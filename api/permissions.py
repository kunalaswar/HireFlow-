from rest_framework.permissions import BasePermission


class IsRecruiter(BasePermission):
    """
    Allows access only to RECRUITER users.
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "RECRUITER"
        )


class IsAdmin(BasePermission):
    """
    Allows access only to ADMIN users.
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "ADMIN"
        )