import django
from django.conf import settings
from django.core.management import BaseCommand


class InitCouchDB(BaseCommand):
    def handle(self, *args, **options):
        django.setup()

        """Create database"""
        response, status_code = settings.COUCHDB_CONNECTION.request("PUT", "")

        if status_code == 412:
            print("CouchDB already setup, exit...")
            exit(0)

        if status_code != 201:
            print("error!")
            print(response, status_code)
            exit(1)
