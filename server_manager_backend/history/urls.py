from django.urls import path, include
from rest_framework import routers
from history.views import ActionHistoryViewSet, ServerInfoViewSet, ServiceHistoryViewSet, BackupHistoryViewSet

router = routers.DefaultRouter()
router.register(r'actions', ActionHistoryViewSet, basename='actionsHistory')
router.register(r'servers', ServerInfoViewSet, basename='serversHistory')
router.register(r'services', ServiceHistoryViewSet, basename='servicesHistory')
router.register(r'backups', BackupHistoryViewSet, basename='backupsHistory')

urlpatterns = [
    path('', include(router.urls))
]
