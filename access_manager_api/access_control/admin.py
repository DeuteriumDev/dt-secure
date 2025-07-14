from django.contrib import admin
from access_control import models
from unfold.admin import ModelAdmin


class ResourcePermissionAdmin(ModelAdmin):
    pass


class UserResourcePermissionAdmin(ModelAdmin):
    # all fields on this model are derived from [ResourcePermissionAdmin]
    def get_readonly_fields(self, request, obj):
        return [a.attname for a in obj._meta.concrete_fields]


admin.site.register(models.ResourcePermission, ResourcePermissionAdmin)
admin.site.register(models.UserResourcePermission, UserResourcePermissionAdmin)
