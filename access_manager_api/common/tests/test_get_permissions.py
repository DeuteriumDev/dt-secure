from django.test import TestCase
from common.get_permissions import get_permission
from accounts.models import CustomUser, CustomGroup, CustomPermissions
from django.contrib.contenttypes.models import ContentType
from documents.models import Folder
from rest_framework.test import APIRequestFactory, force_authenticate
from django.test.client import Client


class GetPermissionTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create(
            email="test@test.ca",
        )
        self.group = CustomGroup.objects.create(
            name="test group",
        )
        self.folder = Folder.objects.create(
            name="test folder",
        )

    def tearDown(self):
        # always cleanup between tests
        CustomPermissions.objects.all().delete()
        Folder.objects.all().delete()
        CustomGroup.objects.all().delete()
        CustomUser.objects.all().delete()

    def test_basic_access(self):
        # arrange
        self.group.members.add(self.user)
        CustomPermissions.objects.create(
            content_type=ContentType.objects.get_for_model(Folder),
            object_id=self.folder.id,
            group=self.group,
            can_delete=True,
        )

        # act
        factory = APIRequestFactory()
        request = factory.get("/")
        request.user = self.user
        result = get_permission(
            request,
            self.folder,
        )

        # assert
        self.assertEqual(result["can_delete"], True)

    def test_inherited_access(self):
        # arrange
        child_folder = Folder.objects.create(
            name="child",
            parent=self.folder,
            inherit_permissions=True,
        )
        self.group.members.add(self.user)
        CustomPermissions.objects.create(
            content_type=ContentType.objects.get_for_model(Folder),
            object_id=self.folder.id,
            group=self.group,
            can_delete=True,
        )

        # act
        factory = APIRequestFactory()
        request = factory.get("/")
        request.user = self.user
        result = get_permission(
            request,
            child_folder,
        )

        # assert
        self.assertEqual(result["can_delete"], True)
