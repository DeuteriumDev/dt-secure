from django.db import models
from .validators import CustomURLValidator


class CustomURLField(models.CharField):
    default_validators = [CustomURLValidator()]
