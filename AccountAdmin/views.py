from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout

from rest_framework import generics, status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .serializer import (
    ClientUserCreateSerializer,
    GymUserSerializer
)
from .permissions import IsSystemAdmin, IsAdminGymUser
from .models import GymUser

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
        })

class GymUserView(viewsets.ModelViewSet):
    queryset = GymUser.objects.all()
    permission_classes = [IsAuthenticated, IsAdminGymUser]
    serializer_class = GymUserSerializer

    def perform_create(self, serializer):
        password = self.request.data.get('password')
        instance = serializer.save()
        if password:
            instance.set_password(password)
            instance.save() #borrar despues 
            
class ClientUserCreateView(generics.CreateAPIView):
    serializer_class = ClientUserCreateSerializer
    permission_classes = [IsAuthenticated, IsSystemAdmin]


