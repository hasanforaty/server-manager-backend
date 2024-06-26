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


class ActionSerializer(serializers.ModelSerializer):
    servers = serializers.SerializerMethodField(read_only=False)

    class Meta:
        model = Action
        fields = ['id', 'name', 'command', 'description', 'interval', 'servers']
        read_only_fields = ['id']

    def get_servers(self, obj):
        servers = obj.server_set.all()  # Get all servers related to this action
        return ServerSerializer(servers, many=True).data



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
