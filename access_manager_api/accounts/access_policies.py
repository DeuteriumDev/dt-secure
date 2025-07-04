from django.http import HttpRequest
from rest_access_policy import AccessPolicy

# from common.get_permissions import get_permission, get_user_permissions
from accounts.models import CustomGroup


class AccountsAccessPolicy(AccessPolicy):
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


class AccountsUsersAccessPolicy(AccessPolicy):
    statements = [
        {
            "action": "*",
            "principal": "admin",
            "effect": "allow",
        },
        {
            "action": ["list"],
            "principal": ["*"],
            "effect": "allow",
        },
        {
            "action": ["retrieve"],
            "principal": ["authenticated"],
            "effect": "allow",
            "condition": "has_read_access",
        },
        {
            "action": ["update", "partial_update"],
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
        {
            "action": "me",
            "principal": ["authenticated"],
            "effect": "allow",
            "condition": "has_read_access",
        },
    ]

    @classmethod
    def scope_queryset(_cls, request: HttpRequest, queryset, model):
        return queryset

    def has_create_access(self, request, view, action) -> bool:
        return request.user.is_admin

    def has_read_access(self, request, view, action) -> bool:
        return True

    def has_update_access(self, request, view, action) -> bool:
        return True

    def has_delete_access(self, request, view, action) -> bool:
        return True


class CustomPermissionsRelationPolicy(AccessPolicy):
    statements = [
        {
            "action": "*",
            "principal": "admin",
            "effect": "allow",
        },
        {
            "action": ["list"],
            "principal": ["*"],
            "effect": "allow",
        },
        {
            "action": ["retrieve"],
            "principal": ["*"],
            "effect": "allow",
            "condition": "has_read_access",
        },
        {
            "action": ["create"],
            "principal": ["*"],
            "effect": "allow",
            "condition": "has_create_access",
        },
        {
            "action": ["update", "partial_update", "destroy"],
            "principal": ["authenticated"],
            "effect": "allow",
            "condition": "has_update_access",
        },
    ]

    @classmethod
    def scope_queryset(_cls, request: HttpRequest, queryset, model):
        return queryset

    def has_create_access(self, request, view, action) -> bool:
        return True

    def has_read_access(self, request, view, action) -> bool:
        return True

    def has_update_access(self, request, view, action) -> bool:
        return True
