from django.urls import path, include
from core.views import ResetTaskView, StopTaskView, RunTaskView, CheckNow

urlpatterns = [
    path('resetTask/', ResetTaskView.as_view(), name='resetTask'),
    path('stopTask/', StopTaskView.as_view(), name='stopTask'),
    path('runTask/', RunTaskView.as_view(), name='runTask'),
    path('runOnce/', CheckNow.as_view(), name='runOnce')
]
