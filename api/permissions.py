from rest_framework.permissions import BasePermission


class IsHR(BasePermission):
    """
    Allows access only to HR users.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "HR"
        )


class IsAdmin(BasePermission):
    """
    Allows access only to Admin users.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "ADMIN"
        )
