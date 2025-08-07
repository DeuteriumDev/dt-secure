from django.contrib import admin
from access_control import models
from unfold.admin import ModelAdmin


class ResourceUserGroupAdmin(ModelAdmin):
    pass


class ResourceUserAdmin(ModelAdmin):
    pass


class ResourcePermissionAdmin(ModelAdmin):
    pass


class ResourceUserPermissionsAdmin(ModelAdmin):
    # all fields on this model are derived from [ResourcePermissionAdmin]
    def get_readonly_fields(self, request, obj):
        return [a.attname for a in obj._meta.concrete_fields]


class EnvironmentAdmin(ModelAdmin):
    model = models.Environment
    readonly_fields = ("token", "created", "updated", "auth_user")

    fieldsets = [
        (
            None,
            {
                "fields": (
                    "name",
                    "created",
                    "updated",
                    "parent_org",
                    "url",
                    "pg_url",
                    "auth_user",
                    "token",
                ),
            },
        ),
    ]


admin.site.register(models.ResourceUser, ResourceUserAdmin)
admin.site.register(models.ResourceUserGroup, ResourceUserGroupAdmin)
admin.site.register(models.ResourcePermission, ResourcePermissionAdmin)
admin.site.register(models.ResourceUserPermissions, ResourceUserPermissionsAdmin)
admin.site.register(models.Environment, EnvironmentAdmin)
