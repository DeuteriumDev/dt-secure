import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.mail import send_mail
from django.utils import timezone
import uuid
from accounts.managers import CustomUserManager
from .fields import CustomURLField
from durin.models import AuthToken, Client
from django.conf import settings
from django.db import connection
from django.core.validators import DomainNameValidator


from access_control.models import UserResourcePermission, ResourcePermission


class CustomGroup(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
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
    hidden = models.BooleanField(default=False, null=False)
    permission = models.OneToOneField(
        ResourcePermission, null=True, on_delete=models.SET_NULL, related_name="group"
    )

    created = models.DateTimeField(null=False, auto_now_add=True)
    updated = models.DateTimeField(null=False, auto_now=True)

    def __str__(self):
        return f"{self.name}"


class Organization(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField("name", blank=False, null=False)
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    root = models.ForeignKey(
        CustomGroup, null=True, blank=False, on_delete=models.SET_NULL
    )
    host = models.CharField(
        validators=[DomainNameValidator()], null=False, blank=False, unique=True
    )

    created = models.DateTimeField(null=False, auto_now_add=True)
    updated = models.DateTimeField(null=False, auto_now=True)

    def __str__(self):
        return f"{self.name}"


class CustomUser(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField("email address", unique=True)
    first_name = models.CharField("first name", max_length=30, blank=True)
    last_name = models.CharField("last name", max_length=30, blank=True)
    date_joined = models.DateTimeField("date joined", default=timezone.now)
    is_active = models.BooleanField("active", default=True)
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    is_staff = models.BooleanField("is staff", default=True)

    # custom attribute for id'ing users created for envs
    is_alias = models.BooleanField(default=False)

    groups = models.ManyToManyField(
        CustomGroup,
        blank=False,
        related_name="members",
    )
    created = models.DateTimeField(null=False, auto_now_add=True)
    updated = models.DateTimeField(null=False, auto_now=True)
    # user_permissions = models.ManyToManyField(
    #     to="auth.Permission",
    #     related_name="custom_users",
    #     blank=True,
    # )

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"
        ordering = ["email"]

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """
        Returns the short name for the user.
        """
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)


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

        uname = auth_user.email.split("@")[0]
        password = str(uuid.uuid4())
        host = kwargs.get("parent_org").host
        port = settings.DATABASES["default"]["PORT"]
        schema = settings.DB_SCHEMA
        name = settings.DB_NAME

        with connection.cursor() as cursor:
            cursor.execute(f"CREATE USER \"{uname}\" WITH PASSWORD '{password}';")
            cursor.execute(
                f'GRANT SELECT ON TABLE "{schema}"."{UserResourcePermission._meta.db_table}" TO "{uname}";'
            )

        instance = super(EnvironmentManager, self).create(
            **kwargs,
            auth_user=auth_user,
            url=settings.HOST_NAME,
            pg_url=f"postgres://{uname}:{password}@{host}:{port}/{name}?schema={schema}",
        )

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
    )

    url = models.URLField(null=False)
    pg_url = CustomURLField(null=False)
    auth_user = models.OneToOneField(
        CustomUser,
        null=False,
        on_delete=models.CASCADE,
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
