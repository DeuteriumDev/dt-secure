from rest_framework import serializers

from .models import Organization, CustomUser, CustomGroup
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes


class CustomUserGroupSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(read_only=True)


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = "__all__"
        depth = 1


class CustomUserSerializer(serializers.ModelSerializer):
    groups = CustomUserGroupSerializer(many=True, read_only=True)
    date_joined = serializers.DateTimeField(read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "email",
            "avatar",
            "first_name",
            "last_name",
            "is_active",
            "groups",
            "date_joined",
        ]


class CustomMembersSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    email = serializers.CharField(read_only=True)
    avatar = serializers.ImageField(read_only=True)
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    date_joined = serializers.DateTimeField(read_only=True)


class CustomGroupSerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()
    members = CustomMembersSerializer(many=True, read_only=True)

    class Meta:
        model = CustomGroup
        fields = "__all__"

    @extend_schema_field(OpenApiTypes.INT)
    def get_member_count(self, obj):
        return obj.members.count()
