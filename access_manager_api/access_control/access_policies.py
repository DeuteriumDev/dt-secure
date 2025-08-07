from django.http import HttpRequest
from rest_access_policy import AccessPolicy

# from common.get_permissions import get_permission, get_user_permissions
from accounts.models import CustomGroup


class AccessControlAccessPolicy(AccessPolicy):
    statements = [
        # {
        #     "action": "*",
        #     "principal": "authenticated",
        #     "effect": "allow",
        # },
        {
            "action": "list",
            "principal": ["authenticated"],
            "effect": "allow",
        },
        {
            "action": ["create"],
            "principal": ["authenticated"],
            "effect": "allow",
            "condition": "has_create_access",
        },
        {
            "action": ["retrieve", "get"],
            "principal": ["authenticated"],
            "effect": "allow",
            "condition": "has_read_access",
        },
        {
            "action": ["update", "partial_update", "members"],
            "principal": ["authenticated"],
            "effect": "allow",
            "condition": "has_update_access",
        },
        {
            "action": ["destroy"],
            "principal": ["authenticated"],
            "effect": "allow",
            "condition": "has_delete_access",
        },
    ]

    @classmethod
    def scope_queryset(_cls, request: HttpRequest, queryset, model):
        return queryset

    def has_create_access(self, request, view, _action) -> bool:
        return True

    def has_read_access(self, request, view, _action) -> bool:
        return True

    def has_update_access(self, request, view, _action) -> bool:
        return True

    def has_delete_access(self, request, view, _action) -> bool:
        return True
