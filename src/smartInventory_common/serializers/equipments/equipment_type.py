from rest_framework import serializers
from .equipment_attribute import EquipmentAttributeSerializer


class EquipmentTypeSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField(max_length=200)
    description = serializers.CharField(max_length=500)

    attributes = serializers.ListSerializer(
        child=EquipmentAttributeSerializer(),
    )

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass
