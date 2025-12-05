import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.mail import send_mail
from django.utils import timezone
import uuid
from django.core.validators import DomainNameValidator

from access_control import mixins
from accounts.managers import CustomUserManager


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

    created = models.DateTimeField(null=False, auto_now_add=True)
    updated = models.DateTimeField(null=False, auto_now=True)

    def __str__(self):
        return f"{self.name}"


class OrganizationManager(mixins.AccessFilterMixin, models.Manager):
    pass


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

    objects = OrganizationManager()

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

    @property
    def uname(self):
        return self.email.split("@")[0]
