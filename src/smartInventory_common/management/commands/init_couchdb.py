import django
from django.conf import settings
from django.core.management import BaseCommand

from smartInventory_common.communication import CouchDB
from smartInventory_common.utils import common_logger

module_logger = common_logger.getChild("InitCouchDB")


class InitCouchDB(BaseCommand):
    """
        Create CouchDB database
    """
    
    def handle(self, *args, **options):
        django.setup()

        """Create database"""
        response, status_code = CouchDB(settings.COUCHDB).request("PUT", "")

        if status_code == 412:
            module_logger.info("CouchDB already setup, exit...")
            exit(0)

        if status_code != 201:
            module_logger.error("error!")
            module_logger.error(response, status_code)
            exit(1)
