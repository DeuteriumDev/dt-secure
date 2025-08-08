import uuid
from django.conf import settings
from django.db import models
from durin.models import AuthToken, Client
from django.conf import settings
from django.db import connection

from accounts.models import CustomUser, CustomGroup, Organization
from .fields import CustomURLField


class EnvironmentManager(models.Manager):
    def create(self, **kwargs):
        auth_user = CustomUser.objects.create(
            email=f"{uuid.uuid4()}@{settings.HOST_NAME}",
            is_staff=False,
            is_alias=True,
        )
        auth_user.set_password(str(uuid.uuid4()))
        auth_user.save()
        client = Client.objects.create(name=kwargs.get("name"))
        client.save()
        token = AuthToken.objects.create(user=auth_user, client=client)
        token.save()

        parent_org = kwargs.get("parent_org")
        security_group = CustomGroup.objects.get_or_create(
            name=f"{parent_org.name} environment users",
            parent=parent_org.root,
            hidden=True,
        )[0]
        auth_user.groups.add(security_group)
        auth_user.save()

        uname = auth_user.email.split("@")[0]
        password = str(uuid.uuid4())
        port = settings.DATABASES["default"]["PORT"]
        schema = settings.DB_SCHEMA
        name = settings.DB_NAME

        with connection.cursor() as cursor:
            cursor.execute(f"CREATE USER \"{uname}\" WITH PASSWORD '{password}';")
            cursor.execute(
                f'GRANT SELECT ON TABLE "{schema}"."{ResourcePermission._meta.db_table}" TO "{uname}";'
            )

        instance = super(EnvironmentManager, self).create(
            **kwargs,
            auth_user=auth_user,
            url=settings.HOST_NAME,
            pg_url=f"postgres://{uname}:{password}@{parent_org.host}:{port}/{name}?schema={schema}",
        )

        default_ug = ResourceUserGroup.objects.create(
            name="default",
            environment=instance,
        )
        default_ug.save()

        return instance


class Environment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField("name", blank=False, null=False)
    created = models.DateTimeField(null=False, auto_now_add=True)
    updated = models.DateTimeField(null=False, auto_now=True)
    description = models.TextField(null=True, blank=True, default="")
    parent_org = models.ForeignKey(
        Organization,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name="environments",
    )

    url = models.URLField(null=False)
    pg_url = CustomURLField(null=False)
    auth_user = models.OneToOneField(
        CustomUser,
        null=False,
        on_delete=models.CASCADE,
        related_name="associated_environment",
    )
    default_resource_group = models.OneToOneField(
        "ResourceUserGroup",  # lazy ref because there are circular relations
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        related_name="+",  # hidden relation
    )

    objects = EnvironmentManager()

    class Meta:
        ordering = ["created"]
        unique_together = ["name", "parent_org"]

    def __str__(self):
        return f"{self.name}"

    @property
    def token(self):
        return AuthToken.objects.get(user=self.auth_user).token

    @property
    def client(self):
        return AuthToken.objects.get(user=self.auth_user).client


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
    environment = models.ForeignKey(
        Environment,
        null=False,
        on_delete=models.CASCADE,
        related_name="environment_groups",
    )

    def __str__(self):
        return f"{self.name}"

    class Meta:
        ordering = ["created"]
        unique_together = ["name", "environment"]


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
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name="environment_users",
    )

    def __str__(self):
        return f"{self.environment} - {self.user_id}"

    class Meta:
        ordering = ["created"]
        unique_together = ["user_id", "environment"]


class ResourceUserPermission(models.Model):
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

        ResourceUserPermission(
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
        ResourceUserPermission,
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
