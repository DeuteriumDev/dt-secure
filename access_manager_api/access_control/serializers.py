from rest_framework import serializers
from access_control import models


class ResourceUserGroupSerializer(serializers.ModelSerializer):
    environment = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = models.ResourceUserGroup
        fields = "__all__"

    def create(self, validated_data):
        return super().create(
            validated_data
            | {
                "environment": models.Environment.objects.get(
                    auth_user=self.context["request"].user
                )
            },
        )


class ResourceUserSerializer(serializers.ModelSerializer):
    groups = ResourceUserGroupSerializer(many=True, read_only=True)
    environment = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = models.ResourceUser
        fields = (
            "id",
            "user_id",
            "created",
            "groups",
            "environment",
        )

    def create(self, validated_data):
        return super().create(
            validated_data
            | {
                "environment": models.Environment.objects.get(
                    auth_user=self.context["request"].user
                )
            },
        )


class ResourceUserPermissionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ResourceUserPermissions
        fields = "__all__"


class ResourcePermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ResourcePermission
        fields = "__all__"


class EnvironmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Environment
        fields = "__all__"
