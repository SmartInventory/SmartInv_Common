from rest_framework import serializers


class InspectionCommentSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)

    comment = serializers.CharField(max_length=512)

    inspection = serializers.UUIDField()

    user = serializers.UUIDField(read_only=True)

    timestamp = serializers.DateTimeField(read_only=True)

    edited = serializers.BooleanField(read_only=True)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass
