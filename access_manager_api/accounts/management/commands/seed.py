from django.conf import settings
from django.core.management.base import BaseCommand
from accounts.models import Organization, CustomGroup, Environment, CustomUser


class Command(BaseCommand):
    help = "Seed application for basic usage"

    def handle(self, *args, **kwargs):
        group = CustomGroup.objects.create(name="Default Group")
        group.members.add(CustomUser.objects.get(email="admin@admin.ca"))
        group.save()
        org = Organization.objects.create(
            name="Default Org",
            root=group,
            host=settings.HOST_NAME, # default hostname
        )
        org.save()

        env = Environment.objects.create(
            name="default",
            parent_org=org,
        )
        env.save()

        self.stdout.write(self.style.SUCCESS("Successfully seeded application"))
