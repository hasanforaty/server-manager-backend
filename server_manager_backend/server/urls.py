from django.urls import path, include
from rest_framework import routers

from server.views import ServerViewSet, ActionsViewSet, ServiceViewSet, DBServiceViewSet, ServerUploadView

router = routers.DefaultRouter()
router.register('server', ServerViewSet, basename='server')
router.register('actions', ActionsViewSet, basename='action')
router.register('service', ServiceViewSet, basename='service')
router.register('serviceDB', DBServiceViewSet, basename='serviceDB')

urlpatterns = [
    path('', include(router.urls)),
    path('upload/', ServerUploadView.as_view(), name='upload')
]
