from common.strtobool import strtobool
from common.filter_mappings import get_filter_mappings, arg_splitter
# from common.mixins import PermissionViewMixin
from .models import CustomGroup, Organization, CustomUser
from .serializers import (
    CustomGroupSerializer,
    OrganizationSerializer,
    CustomUserSerializer,
)
from rest_access_policy import AccessViewSetMixin
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from filters.mixins import FiltersMixin
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from .access_policies import (
    AccountsAccessPolicy,
    AccountsUsersAccessPolicy,
)


group_filters = get_filter_mappings(
    [
        "id__exact",
        "id__in",
        "name__exact",
        "description__exact",
        "parent__exact",
        "parent__in",
        "created__gte",
        "created__lte",
        "updated__gte",
        "updated__lte",
        "parent__isnull",
    ],
    {
        "name__contains": "name__icontains",
        "description__contains": "description__icontains",
    },
)


@extend_schema(
    parameters=[
        OpenApiParameter(name=n, required=False, type=str) for n in group_filters.keys()
    ],
)
class CustomGroupViewSet(
    AccessViewSetMixin, FiltersMixin, viewsets.ModelViewSet
):
    queryset = CustomGroup.objects.all()
    serializer_class = CustomGroupSerializer
    access_policy = AccountsAccessPolicy

    filterset_fields = ["id", "name", "parent", "hidden", "created", "updated"]
    ordering_fields = ["name", "created", "updated"]
    filter_mappings = group_filters
    filter_value_transformations = {
        "id__in": arg_splitter,
        "groups__id__in": arg_splitter,
        "parent__isnull": strtobool,
    }

    def get_queryset(self):
        return self.access_policy.scope_queryset(
            self.request, self.queryset, CustomGroup
        )

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "members": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "format": "uuid",
                        },
                    }
                },
            }
        },
        responses={
            200: {"type": "array", "items": {"type": "string"}},
        },
        operation_id="update_members",
    )
    @action(detail=True, methods=["put"])
    def members(self, request, pk=None):
        group = self.get_object()
        user_ids = request.data.get("members", [])
        group.members.set(user_ids)
        return Response(user_ids)


class OrganizationViewSet(AccessViewSetMixin, viewsets.ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    access_policy = AccountsAccessPolicy


user_filters = get_filter_mappings(
    [
        "id__exact",
        "id__in",
        "first_name__exact",
        "last_name__exact",
        "date_joined",
        "is_active",
        "groups__id__exact",
        "groups__id__in",
    ],
    {
        "first_name__contains": "first_name__icontains",
        "last_name__contains": "last_name__icontains",
        "email__contains": "email__icontains",
    },
)


@extend_schema(
    parameters=[
        OpenApiParameter(name=n, required=False, type=str) for n in user_filters.keys()
    ],
)
class CustomUserViewSet(AccessViewSetMixin, FiltersMixin, viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    access_policy = AccountsUsersAccessPolicy
    filterset_fields = [
        "id",
        "first_name",
        "last_name",
        "date_joined",
        "is_active",
        "email",
    ]
    ordering_fields = ["first_name", "last_name", "date_joined", "is_active", "email"]
    filter_mappings = user_filters
    filter_value_transformations = {
        "id__in": arg_splitter,
        "groups__id__in": arg_splitter,
        "is_active": strtobool,
    }

    def get_queryset(self):
        return self.access_policy.scope_queryset(
            self.request,
            self.queryset,
            CustomGroup,
        )

    @action(detail=False, methods=["GET"])
    def me(self, request):
        return Response(self.get_serializer(request.user, many=False).data)
