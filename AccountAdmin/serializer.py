from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import Group
from .models import GymUser

class GymUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = GymUser
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True}  # oculta el password en la respuesta
        }

    def create(self, validated_data):
        # Usamos pop para sacar el password y pasarlo a set_password()
        password = validated_data.pop('password', None)
        user = GymUser(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user
class ClientUserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    class Meta:
        model = GymUser
        # Sólo los campos que queremos permitir desde el endpoint
        fields = ("username", "email", "password", "first_name", "last_name", "branch")
        extra_kwargs = {
            "branch": {"required": False, "allow_blank": True},
            "email":  {"required": True},
            "username": {"required": True},
        }

    # Validaciones útiles
    def validate_password(self, value):
        validate_password(value)  # usa validadores de Django si los tenés
        return value

    def validate_email(self, value):
        if value and GymUser.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Ese email ya está registrado.")
        return value

    def create(self, validated_data):
        """
        Crea SIEMPRE un usuario 'cliente':
        - sin staff
        - sin superuser
        - rol = 'limMerchant'
        """
        password = validated_data.pop("password")
        user = GymUser.objects.create_user(**validated_data, password=password)
        user.is_staff = False
        user.is_superuser = False
        user.rol = "limMerchant"
        user.save()

        # (opcional) agregar al grupo limMerchant si existe
        try:
            g = Group.objects.get(name="limMerchant")
            user.groups.add(g)
        except Group.DoesNotExist:
            pass

        return user

    def to_representation(self, instance):
        # Respuesta sin password ni flags sensibles
        return {
            "id": instance.id,
            "username": instance.username,
            "email": instance.email,
            "first_name": instance.first_name,
            "last_name": instance.last_name,
            "branch": instance.branch,
            "rol": instance.rol,
        }
