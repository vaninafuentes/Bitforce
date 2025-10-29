# AccountAdmin/views.py
from rest_framework import generics, status, viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .serializer import (
    ClientUserCreateSerializer,
    GymUserSerializer,
    PublicRegisterSerializer,
)
from .permissions import IsSystemAdmin, IsAdminGymUser
from .models import GymUser


# --- Registro público (cliente) ---
class PublicRegisterView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = PublicRegisterSerializer


# --- Logout JWT (blacklist refresh) ---
class LogoutJWTView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh = request.data.get("refresh")
        if not refresh:
            return Response({"detail": "refresh token requerido"}, status=400)
        try:
            token = RefreshToken(refresh)
            token.blacklist()
        except TokenError:
            return Response({"detail": "refresh inválido o ya revocado"}, status=400)
        return Response({"detail": "logout ok"}, status=205)


# --- /me (quién soy) ---
class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        u = request.user
        return Response({
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "rol": getattr(u, "rol", None),
            "is_staff": u.is_staff,
            "is_superuser": u.is_superuser,
            "creditos": getattr(u, "creditos", 0),
            "fecha_vencimiento": getattr(u, "fecha_vencimiento", None),
            "activo": getattr(u, "activo", True),
        })


# --- Admin: gestionar usuarios (GymUser) ---
class GymUserView(viewsets.ModelViewSet):
    queryset = GymUser.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsAdminGymUser]
    serializer_class = GymUserSerializer

    def perform_create(self, serializer):
        password = self.request.data.get("password")
        instance = serializer.save()
        if password:
            instance.set_password(password)
            instance.save(update_fields=["password"])

    # POST /api/AccountAdmin/GymUser/<id>/asignar_creditos/
    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated, IsAdminGymUser])
    def asignar_creditos(self, request, pk=None):
        user = self.get_object()
        # Parseo y validación básica
        try:
            creditos = int(request.data.get("creditos", 0))
            dias = int(request.data.get("dias", 30))
        except (TypeError, ValueError):
            return Response({"detail": "Parámetros inválidos."}, status=status.HTTP_400_BAD_REQUEST)

        if creditos <= 0:
            return Response({"detail": "Los créditos deben ser mayores a 0."}, status=status.HTTP_400_BAD_REQUEST)
        if dias <= 0:
            return Response({"detail": "Los días deben ser mayores a 0."}, status=status.HTTP_400_BAD_REQUEST)

        # Aplica asignación/renovación
        try:
            user.asignar_creditos(creditos, dias)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(self.get_serializer(user).data, status=status.HTTP_200_OK)
    
    # POST /api/AccountAdmin/GymUser/<id>/resetear_creditos/
    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated, IsAdminGymUser])
    def resetear_creditos(self, request, pk=None):
        user = self.get_object()
        user.resetear_creditos()
        return Response({
            "id": user.id,
            "username": user.username,
            "creditos": user.creditos,
            "activo": user.activo,
            "fecha_activacion": user.fecha_activacion,
            "fecha_vencimiento": user.fecha_vencimiento,
            "mensaje": "Créditos reseteados correctamente."
        }, status=status.HTTP_200_OK)


    # GET /api/AccountAdmin/GymUser/<id>/estado_creditos/
    @action(detail=True, methods=["get"], permission_classes=[permissions.IsAuthenticated, IsAdminGymUser])
    def estado_creditos(self, request, pk=None):
        user = self.get_object()
        user.verificar_estado()  # actualiza 'activo' según créditos/vencimiento
        return Response(self.get_serializer(user).data, status=status.HTTP_200_OK)


# --- Admin: crear cliente simplificado ---
class ClientUserCreateView(generics.CreateAPIView):
    serializer_class = ClientUserCreateSerializer
    permission_classes = [permissions.IsAuthenticated, IsSystemAdmin]
