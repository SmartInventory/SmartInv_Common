from rest_framework import serializers

from smartInventory_common.utils.users import UserRoles


class UserSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    username = serializers.CharField(max_length=150)

    first_name = serializers.CharField(max_length=150, allow_blank=True)
    last_name = serializers.CharField(max_length=150, allow_blank=True)
    email = serializers.EmailField(allow_blank=True)

    password = serializers.CharField(write_only=True, max_length=256)

    role = serializers.ChoiceField(UserRoles.choices, allow_blank=True)

    is_staff = serializers.BooleanField()
    is_active = serializers.BooleanField()
    is_superuser = serializers.BooleanField()

    last_login = serializers.DateTimeField()

    date_joined = serializers.DateTimeField()

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass
