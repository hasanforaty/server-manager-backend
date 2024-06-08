from django.urls import path, include
from rest_framework import routers
from history.views import ActionHistoryViewSet
router = routers.DefaultRouter()
router.register(r'actions', ActionHistoryViewSet, basename='actions')

urlpatterns = [
    path('', include(router.urls))
]
