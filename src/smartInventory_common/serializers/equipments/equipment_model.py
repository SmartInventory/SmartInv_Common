from rest_framework import serializers

from .equipment_type import EquipmentTypeSerializer
from .equipment_attribute import EquipmentAttributeSerializer
from smartInventory_common.utils import BorrowType


class EquipmentModelSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    reference = serializers.CharField(max_length=200, allow_blank=True)
    quantity = serializers.IntegerField(required=True)
    name = serializers.CharField(max_length=200)

    description = serializers.CharField(max_length=500, allow_null=True)

    type = serializers.ListSerializer(
        child=EquipmentTypeSerializer(),
        allow_null=True,
        allow_empty=True
    )

    borrow_type = serializers.ChoiceField(
        choices=BorrowType.choices,
        default=BorrowType.NONE,
        allow_null=True
    )

    needs_guarantor = serializers.BooleanField()

    attributes = serializers.ListSerializer(
        child=EquipmentAttributeSerializer()
    )

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass
