# BitforceApp/serializer.py
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from django.utils import timezone
from datetime import timedelta
from zoneinfo import ZoneInfo
from AccountAdmin.models import GymUser

from .models import Branch, Activity, Coach, ClaseProgramada, Booking
from .models import ClaseProgramada, Booking
from django.contrib.auth import get_user_model

User = get_user_model()

# ==== NUEVO: serializer para crear reservas como admin ====
class AdminReserveSerializer(serializers.Serializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    slot = serializers.PrimaryKeyRelatedField(queryset=ClaseProgramada.objects.filter(activo=True))

    def validate(self, data):
        """
        Reglas:
          - si la reserva es manual (admin), por default permitimos aun si pasó el cutoff.
          - sí validamos cupo y duplicados.
        """
        slot = data["slot"]
        # cupo
        actuales = Booking.objects.filter(slot=slot).count()
        if actuales >= slot.capacidad:
            raise serializers.ValidationError("Sin cupos disponibles.")
        # duplicado para ese user
        if Booking.objects.filter(slot=slot, user=data["user"]).exists():
            raise serializers.ValidationError("Ese usuario ya tiene reserva en ese horario.")
        return data 

# ====== TZ local ======
LOCAL_TZ = ZoneInfo("America/Argentina/Mendoza")


class LocalAwareDateTimeField(serializers.DateTimeField):
    """Acepta formatos simples y, si viene sin tz, asume America/Argentina/Mendoza."""
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("input_formats", [
            "%Y-%m-%d %H:%M",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M%z",
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S.%fZ",
        ])
        super().__init__(*args, **kwargs)

    def to_internal_value(self, value):
        dt = super().to_internal_value(value)
        if timezone.is_naive(dt):
            dt = timezone.make_aware(dt, LOCAL_TZ)
        return dt


# -------- Branch --------
class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = ("id", "nombre", "direccion")
        validators = [
            UniqueTogetherValidator(
                queryset=Branch.objects.all(),
                fields=("nombre", "direccion"),
                message="Ya existe una sucursal con ese nombre y dirección."
            )
        ]


# -------- Coach --------
class CoachSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coach
        fields = ("id", "nombre", "especialidad", "email")


# -------- Activity (con contadores) --------
class ActivitySerializer(serializers.ModelSerializer):
    # contadores que anota la view
    slots_count = serializers.IntegerField(read_only=True)
    bookings_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Activity
        fields = (
            "id",
            "nombre",
            "duracion",
            "capacidad_maxima",
            "cutoff_minutes",
            "coach",
            "activo",
            # nuevos:
            "slots_count",
            "bookings_count",
        )

    def validate_duracion(self, v):
        if v <= 0:
            raise serializers.ValidationError("La duración debe ser mayor a 0.")
        return v

    def validate_capacidad_maxima(self, v):
        if v <= 0:
            raise serializers.ValidationError("La capacidad debe ser mayor a 0.")
        return v


# -------- Clase Programada (Slot) --------
# -------- Clase Programada (Slot) --------
class ClaseProgramadaSerializer(serializers.ModelSerializer):
    inicio = LocalAwareDateTimeField()  # ← amigable
    actividad_nombre = serializers.CharField(source="actividad.nombre", read_only=True)
    sucursal_nombre  = serializers.CharField(source="sucursal.nombre", read_only=True)
    sucursal_dir     = serializers.CharField(source="sucursal.direccion", read_only=True)
    fin              = serializers.SerializerMethodField()
    # NUEVO: cantidad de reservas (Booking) para este slot
    reservas_count   = serializers.SerializerMethodField()

    class Meta:
        model  = ClaseProgramada
        fields = (
            "id", "actividad", "actividad_nombre",
            "sucursal", "sucursal_nombre", "sucursal_dir",
            "coach", "inicio", "fin", "capacidad", "cutoff_minutes", "activo",
            "reservas_count",           # ← NUEVO
        )
        validators = [
            UniqueTogetherValidator(
                queryset=ClaseProgramada.objects.all(),
                fields=("actividad", "sucursal", "inicio"),
                message="Ya existe un slot para esa actividad/sucursal/horario."
            )
        ]

    def get_fin(self, obj):
        return obj.fin.isoformat()

    def get_reservas_count(self, obj):
        # related_name='bookings' en Booking.slot
        return obj.bookings.count()

    def validate_capacidad(self, v):
        if v <= 0:
            raise serializers.ValidationError("La capacidad debe ser mayor a 0.")
        return v

    def validate(self, data):
        """
        - No permitir programar en el pasado (create/update)
        - Si no viene 'capacidad', usar por defecto la de la actividad
        """
        from django.utils import timezone
        # obtener el inicio de 'data' o, en update parcial, del instance
        inicio = data.get("inicio", getattr(self.instance, "inicio", None))
        if inicio and inicio <= timezone.now():
            raise serializers.ValidationError({"inicio": "No podés programar clases en el pasado."})

        # capacidad por defecto desde Activity
        if self.instance is None and not data.get("capacidad"):
            actividad = data.get("actividad")
            if actividad:
                data["capacidad"] = actividad.capacidad_maxima

        return data



# -------- Booking (reservas nuevas) --------
class BookingSerializer(serializers.ModelSerializer):
    slot_info = serializers.SerializerMethodField()
    user_info = serializers.SerializerMethodField()

    class Meta:
        model  = Booking
        fields = ("id", "slot", "slot_info", "user_info", "creado")

    def get_slot_info(self, obj):
        s = obj.slot
        return {
            "id": s.id,
            "actividad": s.actividad.nombre,
            "sucursal": f"{s.sucursal.nombre} - {s.sucursal.direccion}",
            "inicio": s.inicio.isoformat(),
            "fin": s.fin.isoformat(),
            "capacidad": s.capacidad,
            "cutoff": s.cutoff,
        }

    def get_user_info(self, obj):
        u = obj.user
        return {
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "rol": getattr(u, "rol", None),
            "is_active": u.is_active,
        }

class ReserveBySlotBookingSerializer(serializers.Serializer):
    slot = serializers.PrimaryKeyRelatedField(queryset=ClaseProgramada.objects.filter(activo=True))

class AdminReserveSerializer(serializers.Serializer):
    user_id = serializers.PrimaryKeyRelatedField(
        source="user", queryset=GymUser.objects.all()
    )
    slot = serializers.PrimaryKeyRelatedField(
        queryset=ClaseProgramada.objects.all()
    )