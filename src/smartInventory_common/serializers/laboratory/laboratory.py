from rest_framework import serializers


class LaboratorySerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(max_length=255)
    description = serializers.CharField(max_length=500, required=False, allow_blank=True, allow_null=True)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass
