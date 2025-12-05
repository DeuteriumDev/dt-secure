import uuid
from django.conf import settings
from django.db import models
from durin.models import AuthToken, Client
from django.conf import settings
from django.db import connection
from psqlextra.manager import PostgresManager

from access_control import mixins, fields
from accounts import models as ac_models


class EnvironmentManager(mixins.AccessFilterMixin, PostgresManager):
    def create(self, **kwargs):
        auth_user = ac_models.CustomUser.objects.create(
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
        security_group = ac_models.CustomGroup.objects.get_or_create(
            name=f"{parent_org.name} environment users",
            parent=parent_org.root,
            hidden=True,
        )[0]
        auth_user.groups.add(security_group)
        auth_user.save()

        uname = auth_user.uname
        password = str(uuid.uuid4())
        port = settings.DATABASES["default"]["PORT"]
        schema = settings.DB_SCHEMA
        name = settings.DB_NAME

        with connection.cursor() as cursor:
            cursor.execute(f"CREATE USER \"{uname}\" WITH PASSWORD '{password}';")
            cursor.execute(
                f'GRANT SELECT ON TABLE "{schema}"."{ResourcePermission._meta.db_table}" TO "{uname}";'
            )

        instance = super().create(
            **kwargs,
            auth_user=auth_user,
            url=settings.HOST_NAME,
            pg_url=f"postgres://{uname}:{password}@{parent_org.host}:{port}/{name}?schema={schema}",
        )

        default_ug = ResourceUserGroup.objects.create(
            name="default",
            description=f'Default Resource User Group created for environment: "{instance.name}"',
            environment=instance,
        )
        default_ug.save()

        instance.default_resource_group = default_ug
        instance.save()

        return instance


class Environment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(null=False, auto_now_add=True)
    updated = models.DateTimeField(null=False, auto_now=True)
    name = models.CharField("name", blank=False, null=False)
    description = models.TextField(null=True, blank=True, default="")
    parent_org = models.ForeignKey(
        ac_models.Organization,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name="environments",
    )

    url = models.URLField(null=False)
    pg_url = fields.CustomURLField(null=False)
    auth_user = models.OneToOneField(
        ac_models.CustomUser,
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
    default_can_create = models.BooleanField(default=True, null=False, blank=False)
    default_can_read = models.BooleanField(default=True, null=False, blank=False)
    default_can_update = models.BooleanField(default=True, null=False, blank=False)
    default_can_delete = models.BooleanField(default=True, null=False, blank=False)

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


class ResourceUserGroupManager(mixins.AccessFilterMixin, PostgresManager):
    pass


class ResourceUserGroup(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    created = models.DateTimeField(null=False, auto_now_add=True)
    updated = models.DateTimeField(null=False, auto_now=True)
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
    environment = models.ForeignKey(
        Environment,
        null=False,
        on_delete=models.CASCADE,
        related_name="environment_groups",
    )

    objects = ResourceUserGroupManager()

    def __str__(self):
        return f"{self.name}"

    class Meta:
        ordering = ["created"]
        unique_together = ["name", "environment"]


class ResourceUserManager(mixins.AccessFilterMixin, PostgresManager):
    def create(self, **kwargs):
        instance = super().create(**kwargs)
        # instance.groups.add()
        return instance


class ResourceUser(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    created = models.DateTimeField(null=False, auto_now_add=True)
    updated = models.DateTimeField(null=False, auto_now=True)

    user_id = models.CharField(null=False, blank=False)
    groups = models.ManyToManyField(
        ResourceUserGroup,
        null=True,
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

    objects = ResourceUserManager()

    def __str__(self):
        return f"{self.environment} - {self.user_id}"

    class Meta:
        ordering = ["created"]
        unique_together = ["user_id", "environment"]


class ResourceManager(mixins.AccessFilterMixin, PostgresManager):
    def create(self, **kwargs):
        instance = super().create(
            **kwargs,
        )

        for user in kwargs.get("group").members:
            ResourceUserPermission.objects.create(
                resource_id=instance.resource_id,
                user=user,
                auth_user=instance.environment.auth_user.uname,
                can_create=kwargs.get("can_create")
                or instance.environment.default_can_create,
                can_read=kwargs.get("can_read")
                or instance.environment.default_can_read,
                can_update=kwargs.get("can_update")
                or instance.environment.default_can_update,
                can_delete=kwargs.get("can_delete")
                or instance.environment.default_can_delete,
            ).save()

        # nav up the tree and add RUPs for each group
        parent = kwargs.get("group").parent
        while parent is not None:
            for user in parent.members:
                ResourceUserPermission.objects.create(
                    resource_id=instance.resource_id,
                    user=user,
                    auth_user=instance.environment.auth_user.uname,
                    can_create=kwargs.get("can_create")
                    or instance.environment.default_can_create,
                    can_read=kwargs.get("can_read")
                    or instance.environment.default_can_read,
                    can_update=kwargs.get("can_update")
                    or instance.environment.default_can_update,
                    can_delete=kwargs.get("can_delete")
                    or instance.environment.default_can_delete,
                ).save()
            parent = parent.parent

        return instance


class Resource(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(null=False, auto_now_add=True)
    updated = models.DateTimeField(null=False, auto_now=True)

    resource_id = models.CharField(null=False, blank=False)
    environment = models.ForeignKey(
        Environment,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name="+",
    )

    objects = ResourceManager()

    class Meta:
        ordering = ["created"]


class ResourceUserPermissionManager(PostgresManager):
    pass


class ResourceUserPermission(models.Model):
    """
    Core read-only (mostly) table that will connect with the customer database to filter queries against.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    user = models.ForeignKey(
        ResourceUser,
        null=True,
        blank=False,
        related_name="+",
        on_delete=models.CASCADE,
    )
    resource = models.ForeignKey(
        Resource,
        null=True,
        blank=False,
        related_name="+",
        on_delete=models.CASCADE,
    )
    auth_user = models.CharField(
        null=False,
        blank=False,
    )

    can_create = models.BooleanField(null=False)
    can_read = models.BooleanField(null=False)
    can_update = models.BooleanField(null=False)
    can_delete = models.BooleanField(null=False)

    objects = ResourceUserPermissionManager()

    class Meta:
        indexes = [
            models.Index(fields=["user"]),
        ]

    def __str__(self):
        return f"{self.user}->{self.resource} - {self.can_create}/{self.can_read}/{self.can_update}/{self.can_delete}"


class ResourcePermissionManager(mixins.AccessFilterMixin, PostgresManager):
    pass


class ResourcePermission(models.Model):
    # default & util columns
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    created = models.DateTimeField(null=False, auto_now_add=True)
    updated = models.DateTimeField(null=False, auto_now=True)
    environment = models.ForeignKey(
        Environment,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name="+",
    )
    resource = models.ForeignKey(
        Resource,
        null=True,
        blank=False,
        related_name="permissions",
        on_delete=models.SET_NULL,
    )

    ## -- inheritable from parent, thus nullable -- ##
    can_create = models.BooleanField(null=True)
    can_read = models.BooleanField(null=True)
    can_update = models.BooleanField(null=True)
    can_delete = models.BooleanField(null=True)

    group = models.ForeignKey(
        ResourceUserGroup,
        null=True,
        on_delete=models.CASCADE,
        related_name="permissions",
    )

    ## -- optional tree w/ inheritance modeling fields -- ##
    parent_permission = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="children_permissions",
        on_delete=models.SET_NULL,
    )
    inherit_from_parent = models.BooleanField(default=False, null=False)

    # optional permission name. EG: "group 1 - r - permissions"
    name = models.CharField("names", blank=True, null=True)

    objects = ResourcePermissionManager()

    class Meta:
        indexes = [
            models.Index(fields=["parent_permission"]),
            models.Index(fields=["group"]),
            # models.Index(fields=["resource", "resource_user_permission"]),
        ]
        # unique_together = ["resource", "resource_user_permission", "environment"]

    def __str__(self):
        if self.inherit_from_parent and self.parent_permission:
            return f"{self.parent_permission.id}/{self.name or self.id} - {self.can_create}/{self.can_read}/{self.can_update}/{self.can_delete}"
        return f"{self.name or self.id} - {self.can_create}/{self.can_read}/{self.can_update}/{self.can_delete}"
