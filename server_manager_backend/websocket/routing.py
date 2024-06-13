from django.urls import path

from . import consumers

ws_urlpatterns = [
    path("ws/serverSummery/", consumers.ServerSummeryConsumer.as_asgi())
]