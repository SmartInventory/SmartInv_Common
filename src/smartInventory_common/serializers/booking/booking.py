from rest_framework import serializers
from smartInventory_common.serializers.utils.validators import no_past


class BookingSerializer(serializers.Serializer):
    id = serializers.UUIDField()

    start_date = serializers.DateTimeField(help_text="Set when equipment scanned")

    end_date = serializers.DateTimeField(allow_null=True, validators=[no_past], help_text="Theoretical time of return")

    restitution_date = serializers.DateTimeField(help_text="Actual time of return")

    borrower_id = serializers.UUIDField()

    physical_id = serializers.CharField(max_length=255)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass
