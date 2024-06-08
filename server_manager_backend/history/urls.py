from django.urls import path, include
from rest_framework import routers
from history.views import ActionHistoryViewSet, ServerInfoViewSet, ServiceHistoryViewSet

router = routers.DefaultRouter()
router.register(r'actions', ActionHistoryViewSet, basename='actionsHistory')
router.register(r'servers', ServerInfoViewSet, basename='serversHistory')
router.register(r'services', ServiceHistoryViewSet, basename='servicesHistory')

urlpatterns = [
    path('', include(router.urls))
]
