from rest_framework import serializers

from smartInventory_common.utils import BorrowType
from .equipment_attribute import EquipmentAttributeSerializer


class EquipmentModelCacheSerializer(serializers.Serializer):
    """
    Serializer used for caching the model for the inventory service
    """

    id = serializers.UUIDField()
    reference = serializers.CharField(max_length=200, allow_blank=True)
    quantity = serializers.IntegerField(required=True)
    name = serializers.CharField(max_length=200)

    description = serializers.CharField(max_length=500, allow_null=True)

    borrow_type = serializers.ChoiceField(choices=BorrowType.choices, default=BorrowType.NONE, allow_null=True)

    type = serializers.CharField(max_length=200, allow_null=True, allow_blank=True, help_text="Name of the model type")

    needs_guarantor = serializers.BooleanField()

    attributes = serializers.ListSerializer(child=EquipmentAttributeSerializer(), allow_null=True, allow_empty=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass
