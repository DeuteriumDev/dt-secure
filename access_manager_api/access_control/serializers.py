from rest_framework import serializers
from access_control import models, fields
from accounts import models as account_models


class ParentResourceUserGroupSerializer(serializers.Serializer):
    """
    To be used for group "parents"
    """

    id = serializers.UUIDField()
    name = serializers.CharField()
    parent = serializers.CharField()
    inherit_from_parent = (
        serializers.BooleanField()
    )  ## denotes wether the associated permission is set to inherit from parent, not the actual group itself


class ResourceUserGroupSerializer(serializers.ModelSerializer):
    environment = serializers.PrimaryKeyRelatedField(
        queryset=models.Environment.objects.filter_by_access(
            request=fields.CurrentRequest(),
            access_defaults=(None, True, None, None),
        ),
        default=fields.CurrentUserEnv(),
    )
    parent = serializers.PrimaryKeyRelatedField(
        queryset=models.ResourceUserGroup.objects.filter_by_access(
            request=fields.CurrentRequest(),
            access_defaults=(None, True, None, None),
        ),
        allow_null=True,
    )
    parents = ParentResourceUserGroupSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = models.ResourceUserGroup
        fields = "__all__"

    def create(self, validated_data):
        env = validated_data.get("environment") or models.Environment.objects.get(
            auth_user=self.context["request"].user
        )
        return super().create(
            validated_data | {"environment": env},
        )


class ResourceUserSerializer(serializers.ModelSerializer):
    groups = ResourceUserGroupSerializer(many=True, required=False)
    environment = serializers.PrimaryKeyRelatedField(
        queryset=models.Environment.objects.filter_by_access(
            request=fields.CurrentRequest(),
            access_defaults=(None, True, None, None),
        ),
        default=fields.CurrentUserEnv(),
    )

    class Meta:
        model = models.ResourceUser
        fields = (
            "id",
            "user_id",
            "created",
            "groups",
            "environment",
        )
        read_only_fields = ("created",)

    def create(self, validated_data):
        env = validated_data.get("environment") or models.Environment.objects.get(
            auth_user=self.context["request"].user
        )
        return super().create(
            validated_data | {"environment": env},
        )


class ResourceUserPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ResourceUserPermission
        fields = "__all__"


class ResourcePermissionSerializer(serializers.ModelSerializer):
    environment = serializers.PrimaryKeyRelatedField(
        queryset=models.Environment.objects.filter_by_access(
            request=fields.CurrentRequest(),
            access_defaults=(None, True, None, None),
        ),
        default=fields.CurrentUserEnv(),
    )

    class Meta:
        model = models.ResourcePermission
        fields = "__all__"


class ResourceSerializer(serializers.ModelSerializer):
    environment = serializers.PrimaryKeyRelatedField(
        queryset=models.Environment.objects.filter_by_access(
            request=fields.CurrentRequest(),
            access_defaults=(None, True, None, None),
        ),
        default=fields.CurrentUserEnv(),
    )

    class Meta:
        model = models.Resource
        fields = "__all__"


class EnvironmentSerializer(serializers.ModelSerializer):
    parent_org = serializers.PrimaryKeyRelatedField(
        queryset=account_models.Organization.objects.filter_by_access(
            request=fields.CurrentRequest(),
            access_defaults=(None, True, None, None),
        ),
        default=fields.CurrentUserEnv(),
    )

    class Meta:
        model = models.Environment
        fields = "__all__"
