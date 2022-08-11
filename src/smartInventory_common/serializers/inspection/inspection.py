from rest_framework import serializers
from django.utils import timezone
from smartInventory_common.serializers.utils.validators import no_past
from smartInventory_common.utils.inspection import InspectionType


class InspectionSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)

    start_date = serializers.DateTimeField(read_only=True, default=serializers.CreateOnlyDefault(timezone.now))

    end_date = serializers.DateTimeField(required=False, allow_null=True, validators=[no_past], read_only=True)

    inspection_type = serializers.ChoiceField(choices=InspectionType.choices, default=InspectionType.REVISION)

    equipment = serializers.UUIDField(read_only=True)

    comments = serializers.ListField(allow_null=True, allow_empty=True)

    created_by = serializers.UUIDField()

    timestamp = serializers.DateTimeField(read_only=True)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass
