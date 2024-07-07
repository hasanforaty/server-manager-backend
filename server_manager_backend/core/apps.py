import os

import schedule
from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        from . import tasks
        if os.environ.get('RUN_MAIN', None) != 'true':
            tasks.start_scheduler()
