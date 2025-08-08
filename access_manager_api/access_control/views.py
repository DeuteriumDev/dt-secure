from rest_framework import viewsets, mixins
from access_control import models, serializers, access_policies
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status


class ResourceUserPermissionViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    queryset = models.ResourceUserPermissions.objects.all()
    serializer_class = serializers.ResourceUserPermissionsSerializer
    access_policy = access_policies.AccessControlAccessPolicy


class ResourceUserViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = models.ResourceUser.objects.all()
    serializer_class = serializers.ResourceUserSerializer
    access_policy = access_policies.AccessControlAccessPolicy

    @action(detail=False, methods=["post"])
    def with_group(self, request):
        group = request.data.pop("group")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if type(group) is str:
            existing_group = models.ResourceUserGroup.objects.get(id=group)
            serializer.save()
            existing_group.members.add(serializer.instance)
            existing_group.save()
        elif type(group) is dict:
            new_group = models.ResourceUserGroup.objects.create(
                **group,
                environment=models.Environment.objects.get(auth_user=self.request.user),
            )
            serializer.save()
            new_group.members.add(serializer.instance)
            new_group.save()

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )


class ResourceUserGroupViewSet(viewsets.ModelViewSet):
    queryset = models.ResourceUserGroup.objects.all()
    serializer_class = serializers.ResourceUserGroupSerializer
    access_policy = access_policies.AccessControlAccessPolicy


class ResourcePermissionViewSet(viewsets.ModelViewSet):
    queryset = models.ResourcePermission.objects.all()
    serializer_class = serializers.ResourcePermissionSerializer
    access_policy = access_policies.AccessControlAccessPolicy


class EnvironmentViewSet(viewsets.ModelViewSet):
    queryset = models.Environment.objects.all()
    serializer_class = serializers.EnvironmentSerializer
    access_policy = access_policies.AccessControlAccessPolicy
