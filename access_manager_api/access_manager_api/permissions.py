from rest_framework.permissions import BasePermission


class AuthPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.auth:
            return False

        return True
