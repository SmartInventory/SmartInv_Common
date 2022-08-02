from rest_framework import serializers


class EquipmentAttributeSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField(max_length=200)
    description = serializers.CharField(max_length=500, required=False, allow_blank=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class EquipmentAttributeValueSerializer(serializers.Serializer):
    id = serializers.UUIDField(write_only=True, required=False)

    name = serializers.CharField(max_length=255, required=False)
    value = serializers.CharField(max_length=255)

    def validate(self, attrs):
        if not attrs.get("id") and not attrs.get("name"):
            raise serializers.ValidationError("specify id or name")
        return super(EquipmentAttributeValueSerializer, self).validate(attrs)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

