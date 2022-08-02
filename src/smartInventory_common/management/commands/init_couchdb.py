import django
from django.conf import settings
from django.core.management import BaseCommand

from smartInventory_common.communication import CouchDB


class InitCouchDB(BaseCommand):
    def handle(self, *args, **options):
        django.setup()

        """Create database"""
        response, status_code = CouchDB(settings.COUCHDB).request("PUT", "")

        if status_code == 412:
            print("CouchDB already setup, exit...")
            exit(0)

        if status_code != 201:
            print("error!")
            print(response, status_code)
            exit(1)
