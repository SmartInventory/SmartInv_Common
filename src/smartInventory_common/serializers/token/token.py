from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class SmartInvObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role
        return token

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass
