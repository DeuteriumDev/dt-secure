from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomGroup, CustomUser, Environment, Organization
from unfold.admin import ModelAdmin
from django.urls import reverse
from django.utils.safestring import mark_safe


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ("email", "first_name", "last_name", "is_staff")
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password", "password_2"),
            },
        ),
    )
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Personal info",
            {
                "fields": (
                    "first_name",
                    "last_name",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    # "user_permissions",
                    "groups",
                ),
            },
        ),
        (
            "Important dates",
            {
                "fields": (
                    "last_login",
                    "date_joined",
                )
            },
        ),
    )
    search_fields = (
        "email",
        "first_name",
        "last_name",
    )
    ordering = ("email",)


class CustomGroupAdmin(ModelAdmin):
    model = CustomGroup
    readonly_fields = (
        "created",
        "updated",
        "group_members",
        "sub_groups",
    )

    fieldsets = [
        (
            None,
            {
                "fields": (
                    "name",
                    "created",
                    "updated",
                    "description",
                    "parent",
                ),
            },
        ),
        (
            None,
            {
                "fields": ("group_members", "sub_groups"),
            },
        ),
    ]

    def group_members(self, obj):
        links = [
            f'<li><a class="text-primary-600 dark:text-primary-500 underline" href="{reverse("admin:accounts_customuser_change", args=(user.id,))}">{user.email}</a></li>'
            for user in obj.members.all()
        ]
        return mark_safe('<ul class="space-y-3">' + "".join(links) + "</ul>")

    def sub_groups(self, obj):
        links = [
            f'<li><a class="text-primary-600 dark:text-primary-500 underline" href="{reverse("admin:accounts_customgroup_change", args=(group.id,))}">{group.name}</a></li>'
            for group in obj.children.all()
        ]
        if len(links) == 0:
            return mark_safe('<p>No sub groups</p>')
        return mark_safe('<ul class="space-y-3">' + "".join(links) + "</ul>")


class OrganizationAdmin(ModelAdmin):
    pass


class EnvironmentAdmin(ModelAdmin):
    model = Environment
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


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(CustomGroup, CustomGroupAdmin)
admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Environment, EnvironmentAdmin)
