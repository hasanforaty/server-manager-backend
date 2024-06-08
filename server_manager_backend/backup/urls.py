from django.urls import path, include
from rest_framework import routers

from backup import views

router = routers.DefaultRouter()
router.register('folder', views.FolderBackupViewSet, basename='folderBackup')

urlpatterns = [
    path('', include(router.urls))
]
