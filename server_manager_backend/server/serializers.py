from rest_framework import serializers

from server.models import Server, Service, DBService, Action


class ActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Action
        fields = '__all__'
        read_only_fields = ['id', ]


class ServerSerializer(serializers.ModelSerializer):
    actions = ActionSerializer(
        many=True,
        required=False
    )

    class Meta:
        model = Server
        fields = ('id', 'name', 'host', 'port', 'username', 'password', 'actions')
        read_only_fields = ['id', ]

    def addOrCreateAction(self, instance, actions):
        for action in actions:
            actionObject, created = Action.objects.get_or_create(action)
            instance.actions.add(actionObject)

    def create(self, validated_data):
        action = validated_data.pop('actions', [])
        server = Server.objects.create(**validated_data)
        self.addOrCreateAction(server, action)
        return server

    def update(self, instance, validated_data):
        action = validated_data.pop('actions', [])
        if action is not None:
            instance.actions.clear()
            self.addOrCreateAction(instance, action)
        for att, value in validated_data.items():
            setattr(instance, att, value)
        instance.save()
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
