from rest_framework import serializers


class EquipmentAttributeSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    description = serializers.CharField(max_length=500, required=False, allow_blank=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class EquipmentAttributeValueSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    value = serializers.CharField(max_length=255)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass
