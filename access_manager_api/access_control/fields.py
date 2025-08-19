from django.db import models
from .validators import CustomURLValidator


class CustomURLField(models.CharField):
    default_validators = [CustomURLValidator()]


class CurrentUserEnv:
    """
    Serializer field. can be None
    """

    requires_context = True

    def __call__(self, serializer_field):
        return serializer_field.context["request"].user.associated_environment or None

    def __repr__(self):
        return "%s()" % self.__class__.__name__


class CurrentRequest:
    """
    Serializer field
    """

    requires_context = True

    def __call__(self, serializer_field):
        return serializer_field.context["request"]

    def __repr__(self):
        return "%s()" % self.__class__.__name__
