from rest_framework import serializers

from core.models import CacheModel


class CacheModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CacheModel
        fields = '__all__'