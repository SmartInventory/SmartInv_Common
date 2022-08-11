from rest_framework import serializers

from smartInventory_common.utils.users import UserRoles


class UserSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=150, allow_blank=True)
    last_name = serializers.CharField(max_length=150, allow_blank=True)
    date_joined = serializers.DateTimeField(required=False)
    is_active = serializers.BooleanField(default=True)
    role = serializers.ChoiceField(choices=UserRoles.choices)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass
