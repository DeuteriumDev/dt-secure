from rest_framework import serializers, mixins
from access_control import models


class ResourceUserSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    

    class Meta:
        model = models.ResourceUser
        fields = "__all__"

    # def update(self, *_args):
    #     raise Exception("Cannot update a [ResourceUser], only create and delete")


class ResourceUserGroupSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = models.ResourceUserGroup
        fields = "__all__"


class ResourceUserPermissionsSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = models.ResourceUserPermissions
        fields = "__all__"


class ResourcePermissionSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = models.ResourcePermission
        fields = "__all__"
