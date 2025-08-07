import uuid
from django.conf import settings
from django.db import models
from accounts.models import Environment


class ResourceUserGroup(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    name = models.CharField("name", blank=False, null=False)
    description = models.TextField(null=True, blank=True, default="")

    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        related_name="children",
        null=True,
        blank=True,
        default=None,
    )
    created = models.DateTimeField(null=False, auto_now_add=True)
    updated = models.DateTimeField(null=False, auto_now=True)

    class Meta:
        ordering = ["created"]


class ResourceUser(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    user_id = models.CharField(null=False, blank=False)
    created = models.DateTimeField(null=False, auto_now_add=True)
    groups = models.ManyToManyField(
        ResourceUserGroup,
        blank=False,
        related_name="members",
    )

    environment = models.ForeignKey(
        Environment,
        null=True,
        blank=False,
        on_delete=models.CASCADE,
        related_name="environment_users",
    )

    class Meta:
        ordering = ["created"]
        unique_together = ["user_id", "environment"]


class ResourceUserPermissions(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    user_id = models.ForeignKey(
        ResourceUser,
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        related_name="resources",
    )
    resource_id = models.CharField(null=False, blank=False)
    environment = models.ForeignKey(
        Environment,
        null=True,
        blank=False,
        on_delete=models.CASCADE,
        related_name="environment_resources",
    )

    can_create = models.BooleanField(null=True)
    can_read = models.BooleanField(null=True)
    can_update = models.BooleanField(null=True)
    can_delete = models.BooleanField(null=True)

    class Meta:
        db_table = settings.RESOURCE_USER_PERMISSIONS_TABLE
        indexes = [
            models.Index(fields=["user_id", "resource_id"]),
        ]


class ResourcePermissionManager(models.Manager):
    def create(self, **kwargs):
        instance = super(ResourcePermissionManager, self).create(
            **kwargs,
        )

        ResourceUserPermissions(
            permission=instance,
            can_create=instance.can_create,
            can_read=instance.can_read,
            can_update=instance.can_update,
            can_delete=instance.can_delete,
        ).save()

        return instance


class ResourcePermission(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    children_permissions = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="parent_permission",
        on_delete=models.SET_NULL,
    )
    resource_id = models.CharField(null=False, blank=False)
    inherit_from_parent = models.BooleanField(default=True, null=False)
    created = models.DateTimeField(null=False, auto_now_add=True)
    updated = models.DateTimeField(null=False, auto_now=True)

    can_create = models.BooleanField(null=True)
    can_read = models.BooleanField(null=True)
    can_update = models.BooleanField(null=True)
    can_delete = models.BooleanField(null=True)
    user_resource = models.OneToOneField(
        ResourceUserPermissions,
        null=False,
        on_delete=models.CASCADE,
        related_name="permission",
    )

    group = models.ForeignKey(
        ResourceUserGroup,
        null=True,
        on_delete=models.SET_NULL,
        related_name="permissions",
    )

    objects = ResourcePermissionManager()

    class Meta:
        indexes = [
            models.Index(fields=["children_permissions"]),
        ]

    def __str__(self):
        if self.inherit_from_parent and self.parent_permission:
            return f"{self.parent_permission.id}/{self.id} - {self.can_create}/{self.can_read}/{self.can_update}/{self.can_delete}"
        return f"{self.id} - {self.can_create}/{self.can_read}/{self.can_update}/{self.can_delete}"
