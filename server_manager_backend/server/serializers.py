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
        print('update is called ')
        action = validated_data.pop('actions', None)
        if action is not None:
            instance.actions.clear()
            self.addOrCreateAction(instance, action)
        for att, value in validated_data.items():
            setattr(instance, att, value)
        instance.save()
        return instance


# class CustomServerSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Server
#         fields = ('id', 'name', 'host', 'port', 'username', 'password')
#         read_only_fields = ['id']

class ActionSerializer(serializers.ModelSerializer):
    servers = serializers.PrimaryKeyRelatedField(many=True, queryset=Server.objects.all())

    class Meta:
        model = Action
        fields = ['id', 'name', 'command', 'description', 'interval', 'servers']
        read_only_fields = ['id']

    def update(self, instance, validated_data):
        servers_data = validated_data.pop('servers', None)

        # Clear existing servers and add updated ones
        if servers_data is not None:
            instance.servers.clear()
            for server_data in servers_data:
                server, created = Server.objects.get_or_create(server_data)
                instance.servers.add(server)
        # print('validated ', validated_data)
        for att, value in validated_data.items():
            # print('set instance', att, ' ', value, ' ', validated_data)
            setattr(instance, att, value)

        # Save the instance
        instance.save()

        # # Ensure the instance is fully refreshed from the database
        # instance.refresh_from_db()
        # print('instance', instance)
        return instance


class ActionGetSerializer(serializers.ModelSerializer):
    servers = ServerSerializer(many=True)

    class Meta:
        model = Action
        fields = ['id', 'name', 'command', 'description', 'interval', 'servers']
        read_only_fields = ['id', 'servers']

    def create(self, validated_data):
        validated_data.pop('servers', None)
        action = Action.objects.create(**validated_data)
        return action


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
