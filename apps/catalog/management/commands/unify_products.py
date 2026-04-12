from django.core.management.base import BaseCommand
from apps.catalog.services.mpn_engine import unify_products_by_mpn


class Command(BaseCommand):
    help = "Unify products by MPN"

    def handle(self, *args, **options):
        unify_products_by_mpn()

        print("MPN unification finished")
