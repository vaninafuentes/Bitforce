# AccountAdmin/jwt_serializers.py
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        t = super().get_token(user)
        # Claims extra útiles para el front:
        t["username"]     = user.username
        t["rol"]          = getattr(user, "rol", None)
        t["is_staff"]     = user.is_staff
        t["is_superuser"] = user.is_superuser
        return t
