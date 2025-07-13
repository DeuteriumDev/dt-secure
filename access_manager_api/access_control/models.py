import uuid
from django.db import models


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
            models.Index(fields=["children_permissions"]),
        ]

    def __str__(self):
        if self.inherit_from_parent and self.parent_permission:
            return f"{self.parent_permission.id}/{self.id} - {self.can_create}/{self.can_read}/{self.can_update}/{self.can_delete}"
        return f"{self.id} - {self.can_create}/{self.can_read}/{self.can_update}/{self.can_delete}"


class UserResourcePermission(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    user_id = models.CharField(null=False, blank=False)
    resource_id = models.CharField(null=False, blank=False)
    can_create = models.BooleanField(null=True)
    can_read = models.BooleanField(null=True)
    can_update = models.BooleanField(null=True)
    can_delete = models.BooleanField(null=True)

    permission = models.ForeignKey(
        ResourcePermission,
        null=False,
        on_delete=models.PROTECT,
        related_name="resources",
    )

    class Meta:
        indexes = [
            models.Index(fields=["user_id", "resource_id"]),
            models.Index(fields=["permission"]),
        ]
