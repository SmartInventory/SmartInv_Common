from rest_framework import serializers

from smartInventory_common.utils import BorrowType


class EquipmentModelSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    reference = serializers.CharField(max_length=200, allow_blank=True)
    quantity = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=200)

    description = serializers.CharField(max_length=500, allow_null=True)

    borrow_type = serializers.ChoiceField(choices=BorrowType.choices, default=BorrowType.NONE, allow_null=True)

    needs_guarantor = serializers.BooleanField()

    attributes_id = serializers.CharField(max_length=255, required=False, read_only=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass
