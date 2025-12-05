import uuid

from django.db.backends.base.operations import BaseDatabaseOperations
from django.db.models import AutoField, UUIDField

BaseDatabaseOperations.integer_field_ranges["UUIDField"] = (0, 0)


# Not used yet, wanted to use as default id field in https://github.com/DeuteriumDev/dt-secure/commit/42b50c8e5969ef762689c931b6ac3945923cfbe0
class UUIDAutoField(UUIDField, AutoField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("default", uuid.uuid4)
        kwargs.setdefault("editable", False)
        super().__init__(*args, **kwargs)
