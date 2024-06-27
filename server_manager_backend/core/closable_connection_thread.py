from django.db import connection
from threading import Thread


class ConnectionThread(Thread):

    def run(self):
        super().run()

        connection.close()
