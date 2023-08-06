import urllib
import time
import os
import os.path
import logging
import zipfile
import optparse
import unicodedata

from django.core.management.base import BaseCommand
from django.utils.encoding import force_unicode

from ...exceptions import *
from ...signals import *
from ...models import *
from ...settings import *
from ...geonames import Geonames


class Command(BaseCommand):
    def skip(self, geoname_id):
        if Country.objects.filter(geoname_id=geoname_id).count():
            return False
        if Region.objects.filter(geoname_id=geoname_id).count():
            return False
        if City.objects.filter(geoname_id=geoname_id).count():
            return False

    def handle(self, *args, **options):
        if not os.path.exists(DATA_DIR):
            self.logger.info('Creating %s' % DATA_DIR)
            os.mkdir(DATA_DIR)

        for url in TRANSLATION_SOURCES:
            geonames = Geonames(url)

            for items in geonames.parse():
                if self.skip(items[1]):
                    continue

                print items
