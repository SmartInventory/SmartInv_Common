from rest_framework import serializers


class EquipmentAttributeSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField(max_length=200)
    description = serializers.CharField(max_length=500)
    initial_value = serializers.CharField(max_length=200, allow_blank=True, allow_null=True, required=False)
    value = serializers.CharField(max_length=200, allow_blank=True, allow_null=True, required=False)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass
