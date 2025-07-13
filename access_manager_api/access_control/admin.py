from django.contrib import admin
from access_control import models
from unfold.admin import ModelAdmin


class ResourcePermissionAdmin(ModelAdmin):
    pass


class UserResourcePermissionAdmin(ModelAdmin):
    pass


admin.site.register(models.ResourcePermission, ResourcePermissionAdmin)
admin.site.register(models.UserResourcePermission, UserResourcePermissionAdmin)
