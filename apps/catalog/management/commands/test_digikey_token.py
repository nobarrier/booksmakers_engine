from django.core.management.base import BaseCommand
from apps.catalog.services.external_api.digikey_auth import get_access_token


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        token = get_access_token()
        print("TOKEN:", token[:40])
