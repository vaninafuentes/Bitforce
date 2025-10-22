# BitforceApp/views.py
from django.db import transaction
from django.utils import timezone
from datetime import timedelta

from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema
from AccountAdmin.permissions import IsSystemAdmin

from .models import Branch, Coach, Activity, ClaseProgramada, Shift
from .serializer import (
    BranchSerializer, CoachSerializer, ActivitySerializer,
    ClaseProgramadaSerializer, ShiftSerializer, ReserveBySlotSerializer
)
from .models import ClaseProgramada, Booking
from .serializer import BookingSerializer, ReserveBySlotBookingSerializer
from AccountAdmin.permissions import IsSystemAdmin

# --- Branch ---
class SucursalView(viewsets.ModelViewSet):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer

    def get_permissions(self):
        # GET/HEAD/OPTIONS: autenticado; POST/PUT/PATCH/DELETE: admin
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsSystemAdmin()]

# --- Coach ---
class CoachView(viewsets.ModelViewSet):
    queryset = Coach.objects.all()
    serializer_class = CoachSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsSystemAdmin()]

# --- Activity ---
class ActividadView(viewsets.ModelViewSet):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsSystemAdmin()]

# --- Clase Programada (slots publicados por admin) ---
class ClaseProgramadaView(viewsets.ModelViewSet):
    queryset = ClaseProgramada.objects.select_related("actividad", "sucursal", "coach")
    serializer_class = ClaseProgramadaSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsSystemAdmin()]
    
    def perform_create(self, serializer):
        obj = serializer.save()
        # seguridad extra (por si algo raro pasa)
        if obj.inicio <= timezone.now():
            raise ValidationError({"inicio": "No podés programar clases en el pasado."})

# --- Shifts (reservas) - sólo lectura desde API ---
class ShiftView(viewsets.ReadOnlyModelViewSet):
    """
    Admin ve todas; cliente ve sólo las suyas.
    La creación va por ReservarPorSlotView.
    """
    serializer_class = ShiftSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Shift.objects.select_related("slot", "slot__actividad", "slot__sucursal", "gymuser")

    def get_queryset(self):
        qs = super().get_queryset()
        u = self.request.user
        if getattr(u, "is_superuser", False) or getattr(u, "rol", "") == "admin" or u.groups.filter(name="admin").exists():
            return qs
        return qs.filter(gymuser=u)

# --- Reservar por slot ---
@extend_schema(
    request=ReserveBySlotSerializer,
    responses={201: ShiftSerializer, 400: None},
    description="Reserva un lugar en una Clase Programada (slot) para el usuario autenticado. "
                "Valida cutoff y cupo por horario."
)
class ReservarPorSlotView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        ser = ReserveBySlotSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        slot = ser.validated_data["slot"]

        # Seguridad extra: si ya empezó o pasó cutoff, cortar (el serializer ya lo controla)
        now = timezone.now()
        if slot.inicio <= now:
            return Response({"detail": "La clase ya inició o finalizó."}, status=status.HTTP_400_BAD_REQUEST)
        cutoff_dt = slot.inicio - timedelta(minutes=slot.cutoff)
        if now > cutoff_dt:
            return Response({"detail": f"Las inscripciones cierran {slot.cutoff} minutos antes del inicio."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Concurrency: bloquear fila al contar
        Shift.objects.select_for_update().filter(slot=slot)

        actuales = Shift.objects.filter(slot=slot).count()
        if actuales >= slot.capacidad:
            return Response({"detail": "Sin cupos disponibles."}, status=status.HTTP_400_BAD_REQUEST)

        obj, created = Shift.objects.get_or_create(gymuser=request.user, slot=slot)
        if not created:
            return Response({"detail": "Ya tenés una reserva para ese horario."}, status=status.HTTP_400_BAD_REQUEST)

        data = ShiftSerializer(obj).data
        data["cupos_restantes"] = max(0, slot.capacidad - (actuales + 1))
        data["cutoff_minutes"] = slot.cutoff
        return Response(data, status=status.HTTP_201_CREATED)

class BookingView(viewsets.ReadOnlyModelViewSet):
    """Listado de reservas en la tabla NUEVA. Admin ve todas; cliente ve las propias."""
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Booking.objects.select_related("slot","user","slot__actividad","slot__sucursal")
        u = self.request.user
        if u.is_superuser or getattr(u, "rol", "") == "admin" or u.groups.filter(name="admin").exists():
            return qs
        return qs.filter(user=u)

class ReservarSlotBookingView(APIView):
    """POST: crea una reserva en la tabla NUEVA (Booking) para el usuario autenticado."""
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        ser = ReserveBySlotBookingSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        slot = ser.validated_data["slot"]
        u    = request.user

        now = timezone.now()
        if slot.inicio <= now:
            return Response({"detail":"La clase ya inició o finalizó."}, status=status.HTTP_400_BAD_REQUEST)

        cutoff = slot.cutoff  # usa override o el de Activity
        if now > slot.inicio - timedelta(minutes=cutoff):
            return Response({"detail": f"Las inscripciones cierran {cutoff} minutos antes del inicio."},
                            status=status.HTTP_400_BAD_REQUEST)

        # cupo (bloqueo optimista)
        Booking.objects.select_for_update().filter(slot=slot)
        actuales = Booking.objects.filter(slot=slot).count()
        if actuales >= slot.capacidad:
            return Response({"detail":"Sin cupos disponibles."}, status=status.HTTP_400_BAD_REQUEST)

        obj, created = Booking.objects.get_or_create(slot=slot, user=u)
        if not created:
            return Response({"detail":"Ya reservaste este horario."}, status=status.HTTP_400_BAD_REQUEST)

        data = BookingSerializer(obj).data
        data["cupos_restantes"] = max(0, slot.capacidad - (actuales + 1))
        return Response(data, status=status.HTTP_201_CREATED)