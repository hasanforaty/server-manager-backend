from rest_framework import serializers

from server.models import Server, Service, DBService, Action


class ServerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Server
        fields = '__all__'
        read_only_fields = ['id', ]


class ServiceSerializer(serializers.ModelSerializer):
    Server = ServerSerializer(
        required=True,

    )

    class Meta:
        model = Service
        fields = '__all__'
        read_only_fields = ['id', ]


class DBServiceSerializer(serializers.ModelSerializer):
    Server = ServerSerializer(
        required=True,

    )

    class Meta:
        model = DBService
        fields = '__all__'
        read_only_fields = ['id', ]


class ActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Action
        fields = '__all__'
        read_only_fields = ['id', ]

    def _createdServer(self, instance, servers):
        for server in servers:
            serverObj, created = Server.objects.get_or_create(server)
            instance.servers.add(serverObj)
            serverObj.actions.add(instance)

    def create(self, validated_data):
        servers = validated_data.pop('servers', [])

        action = Action.objects.create(**validated_data)
        self._createdServer(action, servers)

        return action

    def update(self, instance, validated_data):
        servers = validated_data.pop('servers', [])

        if servers is not None:
            instance.servers.clear()
            self._createdServer(instance, servers)
        for att, value in validated_data.items():
            setattr(instance, att, value)
        instance.save()
        return instance
