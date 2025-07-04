from rest_framework.response import Response
from rest_framework import status
# from accounts.models import CustomPermissions


# class PermissionViewMixin:
#     def destroy(self, request, *args, **kwargs):
#         instance = self.get_object()
#         CustomPermissions.objects.filter(object_id=instance.id).delete()
#         instance.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
