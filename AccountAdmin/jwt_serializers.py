# AccountAdmin/jwt_serializers.py
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Permite autenticarse con username O email usando el mismo campo 'username'.
    Si ingresan un email en 'username', lo mapeamos al username real antes de validar.
    """
    def validate(self, attrs):
        username = attrs.get("username")

        # Si parece un email, intentar mapear al username real
        if username and "@" in username:
            try:
                user = User.objects.get(email__iexact=username)
                # reemplazar por el username (o USERNAME_FIELD si fuera distinto)
                attrs["username"] = getattr(user, User.USERNAME_FIELD, user.username)
            except User.DoesNotExist:
                # si no existe, dejar que la validación falle normalmente
                pass

        return super().validate(attrs)
