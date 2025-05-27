from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login, logout
from .serializer import * 
from rest_framework.response import *
from rest_framework import viewsets
from .models import *
from AccountAdmin.permissions import IsAdminGymUser
#from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny

class GymUserView(viewsets.ModelViewSet):
    queryset = GymUser.objects.all()
    permission_classes = [AllowAny]  # Establece explícitamente los permisos
        #permission_classes = [IsAuthenticated, IsAdminGymUser]
    serializer_class = GymUserSerializer

    def perform_create(self, serializer):
        password = self.request.data.get('password')
        instance = serializer.save()
        if password:
            instance.set_password(password)
            instance.save() #borrar despues 

class LoginView(APIView):
    authentication_classes = []  # Deshabilita la autenticación para esta vista
    permission_classes = []      # Deshabilita los permisos para esta vista
    
    def get(self, request):
        # Retorna un mensaje indicando que esta es la vista de login
        return Response({
            "message": "Utiliza el método POST para iniciar sesión",
            "format": {
                "username": "tu_usuario",
                "password": "tu_contraseña"
            }
        }, status=status.HTTP_200_OK)

    def post(self, request):
        # ...existing code...
        username = request.data.get("username")
        password = request.data.get("password")
        print(username, password)
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return Response({
                "message": "Login exitoso",
                "username": user.username,
                "rol": user.rol,
                "email": user.email,
            }, status=status.HTTP_200_OK)
        return Response({"error": "Credenciales inválidas"}, status=status.HTTP_400_BAD_REQUEST)

# class LoginView(APIView):
#     def post(self, request):
#         username = request.data.get("username")
#         password = request.data.get("password")
#         print(username, password)
#         user = authenticate(request, username=username, password=password)
#         if user is not None:
#             login(request, user)
#             return Response({
#                 "message": "Login exitoso",
#                 "username": user.username,
#                 "rol": user.rol,
#                 "email": user.email,

#             }, status=status.HTTP_200_OK)
#         return Response({"error": "Credenciales inválidas"}, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"message": "Logout exitoso"}, status=status.HTTP_200_OK)


