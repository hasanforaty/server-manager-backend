from rest_framework import serializers

from server.models import Server, Service, DBService, Action


class ServerSerializer(serializers.ModelSerializer):
    # actions = ActionSerializer(
    #     many=True,
    #     required=False
    # )
    actions = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Action.objects.all(),
        required=False,
    )

    class Meta:
        model = Server
        fields = ('id', 'name', 'host', 'port', 'username', 'password', 'actions')
        read_only_fields = ['id', 'actions']

    def addOrCreateAction(self, instance, actions):
        for action in actions:
            actionObject, created = Action.objects.get_or_create(action)
            instance.actions.add(actionObject)

    # def create(self, validated_data):
    #     action = validated_data.pop('actions', [])
    #     server = Server.objects.create(**validated_data)
    #     self.addOrCreateAction(server, action)
    #     return server

    def update(self, instance, validated_data):
        action = validated_data.pop('actions', [])
        if action is not None:
            instance.actions.clear()
            self.addOrCreateAction(instance, action)
        for att, value in validated_data.items():
            setattr(instance, att, value)
        instance.save()
        return instance


class CustomServerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Server
        fields = ('id', 'name', 'host', 'port', 'username', 'password')
        read_only_fields = ['id']


class ActionSerializer(serializers.ModelSerializer):
    servers = CustomServerSerializer(many=True)

    class Meta:
        model = Action
        fields = ['id', 'name', 'command', 'description', 'interval', 'servers']
        read_only_fields = ['id']

    def create(self, validated_data):
        servers_data = validated_data.pop('servers')
        action = Action.objects.create(**validated_data)
        for server_data in servers_data:
            server, created = Server.objects.get_or_create(**server_data)
            action.servers.add(server)
        return action

    def update(self, instance, validated_data):
        servers_data = validated_data.pop('servers')

        instance.name = validated_data.get('name', instance.name)
        instance.command = validated_data.get('command', instance.command)
        instance.description = validated_data.get('description', instance.description)
        instance.interval = validated_data.get('interval', instance.interval)
        instance.save()

        # Clear existing servers and add updated ones
        instance.servers.clear()
        for server_data in servers_data:
            server, created = Server.objects.get_or_create(**server_data)
            instance.servers.add(server)

        return instance


class ServiceSerializer(serializers.ModelSerializer):
    server = serializers.PrimaryKeyRelatedField(
        queryset=Server.objects.all(),
        required=True,
    )

    class Meta:
        model = Service
        fields = '__all__'
        read_only_fields = ['id', 'server']


class DBServiceSerializer(serializers.ModelSerializer):
    server = serializers.PrimaryKeyRelatedField(
        queryset=Server.objects.all(),
        required=True
    )

    class Meta:
        model = DBService
        fields = '__all__'
        read_only_fields = ['id', 'server']


class DBServiceRetrieveSerializer(serializers.ModelSerializer):
    # server = serializers.PrimaryKeyRelatedField(
    #     queryset=Server.objects.all(),
    #     required=True
    # )
    server = ServerSerializer(many=False, read_only=True)

    class Meta:
        model = DBService
        fields = '__all__'
        read_only_fields = ['id', 'server']
