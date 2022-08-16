from rest_framework import serializers


class TokenCurrentUserDefault(serializers.CurrentUserDefault):
    def __call__(self, serializer_field):
        return serializer_field.context["request"].user.pk
