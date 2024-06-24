from django.urls import path, include
from rest_framework import routers

from backup import views

router = routers.DefaultRouter()
router.register(r'folder', views.FolderBackupViewSet, basename='folderBackup')
router.register(r'checkFolder', views.CheckFolderBackupViewSet, basename='checkFolderBackup')

urlpatterns = [
    path('', include(router.urls))
]
