from django.urls import path, include
from rest_framework import routers

from server.views import ServerViewSet, ActionsViewSet

router = routers.DefaultRouter()
router.register('server', ServerViewSet, basename='server')
router.register('action', ActionsViewSet, basename='action')

urlpatterns = [
    path('', include(router.urls))
]
