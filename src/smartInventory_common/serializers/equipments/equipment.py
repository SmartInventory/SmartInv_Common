from rest_framework import serializers

from .equipment_model import EquipmentModelSerializer


class EquipmentSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    model_id = serializers.UUIDField(required=True)
    physical_id = serializers.CharField(max_length=255, required=True)

    model_spec = EquipmentModelSerializer(allow_null=True, read_only=True)

    attributes_id = serializers.CharField(max_length=255, read_only=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass
