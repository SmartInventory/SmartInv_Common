from rest_framework import serializers


class EquipmentAttributeSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField(max_length=200)
    description = serializers.CharField(max_length=500, allow_blank=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass
