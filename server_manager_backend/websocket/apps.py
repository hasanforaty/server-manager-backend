import asyncio
import os
import threading

from django.apps import AppConfig


class WebsocketConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'websocket'

    def ready(self):
        from . import consumers
        if os.environ.get('RUN_MAIN', None) != 'true':
            def start_background_task():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(consumers.periodic_update())

            thread = threading.Thread(target=start_background_task)
            thread.daemon = True
            thread.start()
