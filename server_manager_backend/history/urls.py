from django.urls import path, include
from rest_framework import routers
from history.views import ActionHistoryViewSet, ServerInfoViewSet

router = routers.DefaultRouter()
router.register(r'actions', ActionHistoryViewSet, basename='actionsHistory')
router.register(r'servers', ServerInfoViewSet, basename='serversHistory')

urlpatterns = [
    path('', include(router.urls))
]
