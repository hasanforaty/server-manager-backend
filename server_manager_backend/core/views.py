from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import TaskModel
from core.tasks import restart_scheduler, stop_scheduler, start_scheduler, check_servers


# Create your views here.


class ResetTaskView(APIView):

    def get(self, request):

        try:
            restart_scheduler()
            # start_scheduler()
            # stop_scheduler()
            # print(started)
            return Response({'message': 'Scheduler restarted successfully.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class StopTaskView(APIView):
    def get(self, request):
        try:
            stop_scheduler()
            return Response({'message': 'Scheduler Stopped successfully.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class RunTaskView(APIView):
    def get(self, request):
        try:
            if TaskModel.objects.all().last().active:
                return Response({'message': 'cant Run , it is already running.'}, status=status.HTTP_403_FORBIDDEN)
            start_scheduler()
            return Response({'message': 'Scheduler run successfully.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CheckNow(APIView):
    def get(self, request):
        try:
            if not TaskModel.objects.all().last().active:
                TaskModel(active=True).save()
            check_servers()
            return Response({'message': 'Scheduler run successfully.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
