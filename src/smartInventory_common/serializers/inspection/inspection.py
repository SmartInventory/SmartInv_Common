from rest_framework import serializers

from smartInventory_common.utils import InspectionType


class InspectionSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)

    start_date = serializers.DateTimeField(read_only=True)

    end_date = serializers.DateTimeField(required=False, allow_null=True)

    inspection_type = serializers.ChoiceField(choices=InspectionType.choices, default=InspectionType.REVISION)

    equipment = serializers.UUIDField()

    user = serializers.UUIDField()

    timestamp = serializers.DateTimeField(read_only=True)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass
