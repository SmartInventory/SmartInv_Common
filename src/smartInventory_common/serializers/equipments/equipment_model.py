from rest_framework import serializers

from .equipment_attribute import EquipmentAttributeValueSerializer
from smartInventory_common.utils.equipments import BorrowType


class EquipmentModelSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    reference = serializers.CharField(max_length=200, allow_blank=True)
    quantity = serializers.ReadOnlyField(allow_null=True)
    name = serializers.CharField(max_length=200)

    description = serializers.CharField(max_length=500, allow_null=True)

    borrow_type = serializers.ChoiceField(choices=BorrowType.choices, default=BorrowType.NONE, allow_null=True)

    needs_guarantor = serializers.BooleanField()

    attributes_id = serializers.CharField(max_length=255, required=False)

    attributes = EquipmentAttributeValueSerializer(required=False, many=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass
