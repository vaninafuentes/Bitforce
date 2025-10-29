# AccountAdmin/serializer.py
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueValidator


User = get_user_model()


class PublicRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all(), message="Ese email ya está registrado.")]
    )
    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all(), message="Ese nombre de usuario ya existe.")]
    )

    class Meta:
        model = User
        fields = ("id", "username", "email", "password")

    def validate_password(self, value):
        # aplica validadores de Django si están configurados (min length, etc.)
        validate_password(value)
        return value

    def validate(self, attrs):
        attrs["rol"] = "limMerchant"  # rol por defecto
        return attrs

    def create(self, validated):
        password = validated.pop("password")
        user = User(**validated)
        user.set_password(password)
        user.is_active = False  # queda pendiente de activación por admin
        user.save()
        return user


class GymUserSerializer(serializers.ModelSerializer):
    # password solo escritura; no es obligatorio en update
    password = serializers.CharField(write_only=True, required=False, allow_blank=False)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "rol",
            "branch",
            # --- Créditos ---
            "creditos",
            "fecha_activacion",
            "fecha_vencimiento",
            "activo",
            # flags de Django (útiles para admin)
            "is_active",
            "is_superuser",
            "is_staff",
            # password write-only
            "password",
        ]
        read_only_fields = [
            "fecha_activacion",
            "fecha_vencimiento",
            "activo",
            "is_superuser",
            "is_staff",
        ]
        extra_kwargs = {
            "email": {"required": False, "allow_blank": True},
        }

    def create(self, validated_data):
        # Usa create_user para respetar validaciones internas
        password = validated_data.pop("password", None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        # Si viene password, hashearlo correctamente
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class ClientUserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    class Meta:
        model = User
        # Sólo los campos que queremos permitir desde el endpoint admin de creación de cliente
        fields = ("username", "email", "password", "first_name", "last_name", "branch")
        extra_kwargs = {
            "branch": {"required": False, "allow_blank": True},
            "email": {"required": True},
            "username": {"required": True},
        }

    # Validaciones útiles
    def validate_password(self, value):
        validate_password(value)  # usa validadores de Django si están configurados
        return value

    def validate_email(self, value):
        if value and User.objects.filter(email__iexact=value).exists():
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
        user = User.objects.create_user(**validated_data, password=password)
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
