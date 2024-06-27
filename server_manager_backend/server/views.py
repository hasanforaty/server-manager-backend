from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter, OpenApiResponse, OpenApiExample
from rest_framework import viewsets, mixins, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
import pandas as pd

from server.models import Server, Action, Service, DBService
from server.serializers import ServerSerializer, ActionGetSerializer, ServiceSerializer, DBServiceSerializer, \
    DBServiceRetrieveSerializer, ActionSerializer


# Create your views here.

class ServerViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
):
    queryset = Server.objects.all()
    serializer_class = ServerSerializer
    pagination_class = None


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name="serverId",
                type=OpenApiTypes.UUID,
                description="actions of certen server",
                required=False,
                location=OpenApiParameter.QUERY
            )
        ]
    )
)
class ActionsViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
):
    queryset = Action.objects.all()
    serializer_class = ActionGetSerializer
    pagination_class = None

    # def get_queryset(self):
    #     queryset = self.queryset
    #     serverId = self.request.query_params.get('serverId')
    #     try:
    #         if serverId is not None:
    #             queryset = queryset.filter(servers__id=serverId)
    #     except Exception as e:
    #         raise ValidationError(e)
    #     return queryset
    def get_queryset(self):
        queryset = super().get_queryset()
        serverId = self.request.query_params.get('serverId')

        if serverId:
            try:
                queryset = queryset.filter(servers__id=serverId)
            except Exception as e:
                raise ValidationError(e)

        return queryset

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return ActionGetSerializer
        else:
            return ActionSerializer


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name="serverId",
                type=OpenApiTypes.UUID,
                description="DB's for that server ",
                required=False,
                location=OpenApiParameter.QUERY
            )
        ]
    )
)
class ServiceViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    pagination_class = None

    def get_queryset(self):
        queryset = super().get_queryset()
        serverId = self.request.query_params.get('serverId')
        try:
            if serverId is not None:
                queryset = queryset.filter(server_id=serverId)
        except Exception as e:
            raise ValidationError(e)
        return queryset


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name="backup",
                type=OpenApiTypes.BOOL,
                description="DB's with backup on ",
                required=False,
                location=OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                name="serverId",
                type=OpenApiTypes.UUID,
                description="DB's for that server ",
                required=False,
                location=OpenApiParameter.QUERY
            )
        ]
    )
)
class DBServiceViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
):
    queryset = DBService.objects.all()
    serializer_class = DBServiceSerializer
    pagination_class = None

    def get_queryset(self):
        queryset = super().get_queryset()
        is_backup = self.request.query_params.get('backup')
        serverId = self.request.query_params.get('serverId')
        try:
            if is_backup is not None:
                backup = is_backup.lower() == 'true'
                queryset = queryset.filter(backup=backup)
            if serverId is not None:
                queryset = queryset.filter(server_id=serverId)
        except Exception as e:
            raise ValidationError(e)
        return queryset

    def get_serializer(self, *args, **kwargs):
        if self.action == 'retrieve' or self.action == 'list':
            return DBServiceRetrieveSerializer(*args, **kwargs)
        else:
            return DBServiceSerializer(*args, **kwargs)

@extend_schema_view(
    post=extend_schema(
        description="Upload an Excel file to create multiple Server entries.",
        request={"multipart/form-data": {"type": "object", "properties": {"file": {"type": "string", "format": "binary"}}}},
        responses={
            201: OpenApiResponse(description="Servers created successfully."),
            400: OpenApiResponse(description="Bad request."),
        },
        examples=[
            OpenApiExample(
                "Example 1",
                value={
                    "file": "file content"
                },
                request_only=True,
                response_only=False
            ),
        ],
    ),
)
class ServerUploadView(APIView):
    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file')
        if not file:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            df = pd.read_excel(file)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        errors = []
        for index, row in df.iterrows():
            server_data = {
                "name": row.get("host"),
                "host": row.get("ip/domain"),
                "port": row.get("port"),
                "username": row.get("user"),
                "password": row.get("password"),
            }
            serializer = ServerSerializer(data=server_data)
            if serializer.is_valid():
                serializer.save()
            else:
                errors.append({index: serializer.errors})

        if errors:
            return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "Servers created successfully"}, status=status.HTTP_201_CREATED)