# BitforceApp/views.py
from datetime import timedelta

from django.db import transaction
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone

from rest_framework import mixins, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_spectacular.utils import extend_schema

from AccountAdmin.permissions import IsSystemAdmin

from .models import Activity, Booking, Branch, ClaseProgramada, Coach
from .serializer import (
    ActivitySerializer,
    AdminReserveSerializer,
    BookingSerializer,
    BranchSerializer,
    ClaseProgramadaSerializer,
    CoachSerializer,
    ReserveBySlotBookingSerializer,
)
from rest_framework.decorators import action


def _overlap(a_start, a_end, b_start, b_end):
    return a_start < b_end and b_start < a_end

# --- Branch ---
class SucursalView(viewsets.ModelViewSet):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer

    def get_permissions(self):
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


# --- Activity (con contadores y delete protegido) ---
class ActividadView(viewsets.ModelViewSet):
    serializer_class = ActivitySerializer

    def get_queryset(self):
        return (
            Activity.objects.annotate(
                slots_count=Count("slots", distinct=True),
                bookings_count=Count("slots__bookings", distinct=True),
            )
        )

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsSystemAdmin()]

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if getattr(obj, "slots_count", 0) > 0 or getattr(obj, "bookings_count", 0) > 0:
            return Response(
                {
                    "detail": (
                        "No se puede eliminar esta actividad porque tiene "
                        "clases programadas y/o reservas asociadas. "
                        "Primero eliminá esas clases y reservas."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().destroy(request, *args, **kwargs)

# --- Clase Programada ---
class ClaseProgramadaView(viewsets.ModelViewSet):
    serializer_class = ClaseProgramadaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = (
            ClaseProgramada.objects
            .select_related("actividad", "sucursal", "coach")
        )

        # 🔹 Filtros opcionales
        sucursal = self.request.query_params.get("sucursal")
        actividad = self.request.query_params.get("actividad")
        date_str = self.request.query_params.get("date")  # YYYY-MM-DD

        if sucursal:
            qs = qs.filter(sucursal_id=sucursal)
        if actividad:
            qs = qs.filter(actividad_id=actividad)
        if date_str:
            qs = qs.annotate(inicio_fecha=TruncDate("inicio")).filter(inicio_fecha=date_str)

        # 🔹 Solo futuras (ópt-in): ?only_future=1
        only_future = self.request.query_params.get("only_future")
        if only_future in ("1", "true", "True"):
            qs = qs.filter(inicio__gt=timezone.now())

        # 🔹 Orden
        ordering = self.request.query_params.get("ordering") or "inicio"
        return qs.order_by(ordering)

    @action(detail=True, methods=["get"], permission_classes=[permissions.IsAuthenticated])
    def reservas(self, request, pk=None):
        qs = Booking.objects.select_related("user", "slot").filter(slot_id=pk)
        data = BookingSerializer(qs, many=True).data
        return Response(data, status=200)


    def get_permissions(self):
        # Lecturas: cualquier usuario autenticado
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.IsAuthenticated()]
        # Altas/bajas/edits: solo admin del sistema
        return [permissions.IsAuthenticated(), IsSystemAdmin()]


# --- Booking (tabla nueva) ---
class BookingView(
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """
    Listado de reservas y cancelación (DELETE).
    Admin ve todo; cliente ve solo las propias.
    Filtro opcional: ?date=YYYY-MM-DD (por fecha del inicio del slot).
    """
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Booking.objects.select_related("slot", "user", "slot__actividad", "slot__sucursal")

    def get_queryset(self):
        qs = Booking.objects.select_related("slot", "user", "slot__actividad", "slot__sucursal")

        u = self.request.user
        es_admin = getattr(u, "is_superuser", False) or getattr(u, "rol", "") == "admin"
        if not es_admin:
            qs = qs.filter(user=u)

        slot_id = self.request.query_params.get("slot")
        if slot_id:
            qs = qs.filter(slot_id=slot_id)

        

        date_str = self.request.query_params.get("date")  # YYYY-MM-DD
        if date_str:
            qs = qs.annotate(inicio_fecha=TruncDate("slot__inicio")).filter(inicio_fecha=date_str)

        return qs.order_by("slot__inicio") 


    def destroy(self, request, *args, **kwargs):
        booking = self.get_object()
        u = request.user

        # Solo el dueño o admin puede cancelar
        es_admin = getattr(u, "is_superuser", False) or getattr(u, "rol", "") == "admin"
        if booking.user_id != u.id and not es_admin:
            return Response({"detail": "No podés cancelar esta reserva."}, status=status.HTTP_403_FORBIDDEN)

        # Cutoff: clientes respetan cutoff; admin puede forzar
        slot = booking.slot
        cutoff_min = slot.cutoff_minutes if slot.cutoff_minutes is not None else slot.actividad.cutoff_minutes
        cutoff_min = cutoff_min or 0
        limite = slot.inicio - timedelta(minutes=cutoff_min)
        if timezone.now() >= limite and not es_admin:
            return Response({"detail": "Ya no se puede cancelar (cutoff)."}, status=status.HTTP_400_BAD_REQUEST)

        # (opcional) devolver crédito aquí si corresponde…
        # try:
        #     booking.user.devolver_credito()
        # except AttributeError:
        #     pass

        booking.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    request=ReserveBySlotBookingSerializer,
    responses={201: BookingSerializer, 400: None},
    description="El usuario autenticado reserva un lugar en un slot. Valida cutoff y cupos."
)
class ReservarSlotBookingView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        ser = ReserveBySlotBookingSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        slot = ser.validated_data["slot"]
        u    = request.user

        now = timezone.now()
        if slot.inicio <= now:
            return Response({"detail": "La clase ya inició o finalizó."}, status=status.HTTP_400_BAD_REQUEST)

        cutoff = slot.cutoff
        if now > slot.inicio - timedelta(minutes=cutoff):
            return Response(
                {"detail": f"Las inscripciones cierran {cutoff} minutos antes del inicio."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ✅ BLOQUEAR SOLAPES (usuario ya tiene otra reserva que pisa este horario)
        new_start, new_end = slot.inicio, slot.fin
        existing = Booking.objects.select_related("slot").filter(user=u)
        for b in existing:
            if _overlap(new_start, new_end, b.slot.inicio, b.slot.fin):
                return Response({"detail": "Ya tenés una reserva que se solapa con este horario."},
                                status=status.HTTP_400_BAD_REQUEST)

        # Cupo (bloqueo optimista)
        Booking.objects.select_for_update().filter(slot=slot)
        actuales = Booking.objects.filter(slot=slot).count()
        if actuales >= slot.capacidad:
            return Response({"detail": "Sin cupos disponibles."}, status=status.HTTP_400_BAD_REQUEST)

        obj, created = Booking.objects.get_or_create(slot=slot, user=u)
        if not created:
            return Response({"detail": "Ya reservaste este horario."}, status=status.HTTP_400_BAD_REQUEST)

        data = BookingSerializer(obj).data
        data["cupos_restantes"] = max(0, slot.capacidad - (actuales + 1))
        return Response(data, status=status.HTTP_201_CREATED)



@extend_schema(
    request=AdminReserveSerializer,
    responses={201: BookingSerializer, 400: None},
    description="Admin crea una reserva para un usuario y un slot. Valida cupos y duplicados. No aplica cutoff."
)
class AdminCreateBookingView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsSystemAdmin]

    @transaction.atomic
    def post(self, request):
        ser = AdminReserveSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        slot = ser.validated_data["slot"]
        user = ser.validated_data["user"]

        now = timezone.now()
        new_start, new_end = slot.inicio, slot.fin

        # ✅ Si es futuro, bloquear solapes y respetar cupos
        if new_start > now:
            existing = Booking.objects.select_related("slot").filter(user=user)
            for b in existing:
                if _overlap(new_start, new_end, b.slot.inicio, b.slot.fin):
                    return Response({"detail": "Ese usuario ya tiene una reserva que se solapa con este horario."},
                                    status=status.HTTP_400_BAD_REQUEST)

            Booking.objects.select_for_update().filter(slot=slot)
            actuales = Booking.objects.filter(slot=slot).count()
            if actuales >= slot.capacidad:
                return Response({"detail": "Sin cupos disponibles."}, status=status.HTTP_400_BAD_REQUEST)

        obj, created = Booking.objects.get_or_create(slot=slot, user=user)
        if not created:
            return Response({"detail": "El usuario ya tiene reserva en ese horario."}, status=status.HTTP_400_BAD_REQUEST)

        data = BookingSerializer(obj).data
        return Response(data, status=status.HTTP_201_CREATED)

