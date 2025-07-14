import uuid
from django.db import models


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

    class Meta:
        indexes = [
            models.Index(fields=["user_id", "resource_id"]),
        ]


class ResourcePermissionManager(models.Manager):
    def create(self, **kwargs):
        instance = super(ResourcePermissionManager, self).create(
            **kwargs,
        )

        UserResourcePermission(
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
        UserResourcePermission,
        null=False,
        on_delete=models.CASCADE,
        related_name="permission",
    )

    ## group = relational field to [CustomGroup](../accounts/models.py) model
    objects = ResourcePermissionManager()

    class Meta:
        indexes = [
            models.Index(fields=["children_permissions"]),
        ]

    def __str__(self):
        if self.inherit_from_parent and self.parent_permission:
            return f"{self.parent_permission.id}/{self.id} - {self.can_create}/{self.can_read}/{self.can_update}/{self.can_delete}"
        return f"{self.id} - {self.can_create}/{self.can_read}/{self.can_update}/{self.can_delete}"
