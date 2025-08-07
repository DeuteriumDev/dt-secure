from rest_framework import viewsets, mixins
from access_control import models, serializers, access_policies


class ResourceUserPermissionViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    queryset = models.ResourceUserPermissions.objects.all()
    serializer_class = serializers.ResourceUserPermissionsSerializer
    access_policy = access_policies.AccessControlAccessPolicy


class ResourceUserViewSet(
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = models.ResourceUser.objects.all()
    serializer_class = serializers.ResourceUserSerializer
    access_policy = access_policies.AccessControlAccessPolicy


class ResourceUserGroupViewSet(viewsets.ModelViewSet):
    queryset = models.ResourceUserGroup.objects.all()
    serializer_class = serializers.ResourceUserGroupSerializer
    access_policy = access_policies.AccessControlAccessPolicy


class ResourcePermissionViewSet(viewsets.ModelViewSet):
    queryset = models.ResourcePermission.objects.all()
    serializer_class = serializers.ResourcePermissionSerializer
    access_policy = access_policies.AccessControlAccessPolicy
