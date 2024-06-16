from django.shortcuts import render
from rest_framework import viewsets, mixins
from rest_framework.pagination import PageNumberPagination

from server.models import Server, Action, Service, DBService
from server.serializers import ServerSerializer, ActionSerializer, ServiceSerializer, DBServiceSerializer


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


class ActionsViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
):
    queryset = Action.objects.all()
    serializer_class = ActionSerializer


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
