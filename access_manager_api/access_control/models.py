import uuid
from django.db import models


class UserResourcePermission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.CharField(null=False, blank=False)
    resource_id = models.CharField(null=False, blank=False)
    can_create = models.BooleanField(null=True)
    can_read = models.BooleanField(null=True)
    can_update = models.BooleanField(null=True)
    can_delete = models.BooleanField(null=True)

    class Meta:
        indexes = [
            models.Index(fields=["user_id", "resource_id"]),
        ]


class ResourcePermission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    resources = models.ForeignKey(
        UserResourcePermission,
        null=True,
        on_delete=models.SET_NULL,
        related_name="permission",
    )
    children_permissions = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="parent_permission",
        on_delete=models.SET_NULL,
    )
    inherit_from_parent = models.BooleanField(default=True, null=False)
    created = models.DateTimeField(null=False, auto_now_add=True)
    updated = models.DateTimeField(null=False, auto_now=True)

    can_create = models.BooleanField(null=True)
    can_read = models.BooleanField(null=True)
    can_update = models.BooleanField(null=True)
    can_delete = models.BooleanField(null=True)

    # group = relational field to group model

    class Meta:
        indexes = [
            models.Index(fields=["resources"]),
            models.Index(fields=["children_permissions"]),
        ]
