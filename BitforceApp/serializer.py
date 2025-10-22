# BitforceApp/serializer.py
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from django.utils import timezone
from datetime import timedelta
from zoneinfo import ZoneInfo

from .models import Branch, Activity, Coach, ClaseProgramada, Shift, Booking

# ====== TZ local ======
LOCAL_TZ = ZoneInfo("America/Argentina/Mendoza")


class LocalAwareDateTimeField(serializers.DateTimeField):
    """Acepta formatos simples y, si viene sin tz, asume America/Argentina/Mendoza."""
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("input_formats", [
            "%Y-%m-%d %H:%M",        # 2025-12-01 20:00
            "%Y-%m-%d %H:%M:%S",     # 2025-12-01 20:00:00
            "%Y-%m-%dT%H:%M",        # 2025-12-01T20:00
            "%Y-%m-%dT%H:%M:%S",     # 2025-12-01T20:00:00
            "%Y-%m-%dT%H:%M%z",      # 2025-12-01T20:00-03:00
            "%Y-%m-%dT%H:%M:%S%z",   # 2025-12-01T20:00:00-03:00
            "%Y-%m-%dT%H:%M:%SZ",    # 2025-12-01T23:00:00Z
            "%Y-%m-%dT%H:%M:%S.%fZ", # 2025-12-01T23:00:00.000Z
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


# -------- Activity --------
class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = ("id", "nombre", "duracion", "capacidad_maxima", "cutoff_minutes", "coach", "activo")

    def validate_duracion(self, v):
        if v <= 0:
            raise serializers.ValidationError("La duración debe ser mayor a 0.")
        return v

    def validate_capacidad_maxima(self, v):
        if v <= 0:
            raise serializers.ValidationError("La capacidad debe ser mayor a 0.")
        return v


# -------- Clase Programada (Slot) --------
class ClaseProgramadaSerializer(serializers.ModelSerializer):
    inicio = LocalAwareDateTimeField()  # ← amigable
    actividad_nombre = serializers.CharField(source="actividad.nombre", read_only=True)
    sucursal_nombre  = serializers.CharField(source="sucursal.nombre", read_only=True)
    sucursal_dir     = serializers.CharField(source="sucursal.direccion", read_only=True)
    fin              = serializers.SerializerMethodField()

    class Meta:
        model  = ClaseProgramada
        fields = (
            "id", "actividad", "actividad_nombre",
            "sucursal", "sucursal_nombre", "sucursal_dir",
            "coach", "inicio", "fin", "capacidad", "cutoff_minutes", "activo"
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

    def validate_capacidad(self, v):
        if v <= 0:
            raise serializers.ValidationError("La capacidad debe ser mayor a 0.")
        return v

    def validate(self, data):
        # Por defecto, capacidad = capacidad_maxima de la actividad
        if self.instance is None and not data.get("capacidad"):
            data["capacidad"] = data["actividad"].capacidad_maxima
        return data

    def validate(self, data):
        """
        - No permitir programar en el pasado (create/update)
        - Si no viene 'capacidad', usar por defecto la de la actividad
        """
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

# -------- Shift (lectura) --------
class ShiftSerializer(serializers.ModelSerializer):
    slot_info = ClaseProgramadaSerializer(source="slot", read_only=True)

    class Meta:
        model  = Shift
        fields = ("id", "slot", "slot_info", "creado")


# -------- Reservar por Slot --------
class ReserveBySlotSerializer(serializers.Serializer):
    slot = serializers.PrimaryKeyRelatedField(queryset=ClaseProgramada.objects.filter(activo=True))

    def validate(self, data):
        slot = data["slot"]
        now  = timezone.now()
        if slot.inicio <= now:
            raise serializers.ValidationError("La clase ya inició o finalizó.")
        cutoff_dt = slot.inicio - timedelta(minutes=slot.cutoff)
        if now > cutoff_dt:
            raise serializers.ValidationError(
                f"Las inscripciones cierran {slot.cutoff} minutos antes del inicio."
            )
        return data

from rest_framework import serializers
from .models import ClaseProgramada, Booking

class BookingSerializer(serializers.ModelSerializer):
    slot_info = serializers.SerializerMethodField()

    class Meta:
        model  = Booking
        fields = ("id", "slot", "slot_info", "creado")

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

class ReserveBySlotBookingSerializer(serializers.Serializer):
    slot = serializers.PrimaryKeyRelatedField(queryset=ClaseProgramada.objects.filter(activo=True))
