from rest_framework import serializers

from smartInventory_common.serializers.utils.validators import no_past
from smartInventory_common.utils import InspectionType


class InspectionSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)

    start_date = serializers.DateTimeField(read_only=True)

    end_date = serializers.DateTimeField(required=False, allow_null=True, validators=[no_past])

    inspection_type = serializers.ChoiceField(
        read_only=True, choices=InspectionType.choices, default=InspectionType.REVISION
    )

    equipment = serializers.UUIDField(read_only=True)

    comments = serializers.ListField(allow_null=True, allow_empty=True)

    user = serializers.UUIDField(read_only=True)

    timestamp = serializers.DateTimeField(read_only=True)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass
