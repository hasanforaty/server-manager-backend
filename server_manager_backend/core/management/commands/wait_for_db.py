import time

from django.core.management import BaseCommand
from django.db import OperationalError
from psycopg2 import OperationalError as PsycopgOperationalError


class Command(BaseCommand):
    help = 'Wait for database to be available'

    def handle(self, *args, **options):
        self.stdout.write('Waiting for database to be available')
        db_up = False
        while not db_up:
            try:
                self.check(databases=['default'])
                db_up = True
            except (OperationalError, PsycopgOperationalError):
                self.stdout.write('database not available, waiting 1 seconds.....')
                time.sleep(1)
        self.stdout.write('database is available')
