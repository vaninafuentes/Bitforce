from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login, logout
from rest_framework.permissions import IsAuthenticated

from .serializer import * 
from rest_framework.response import *
from rest_framework import viewsets
from .models import *

class GymUserViewSet(viewsets.ModelViewSet):
    queryset = GymUser.objects.all()
    serializer_class = GymUserSerializer

class LoginView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        print(username, password)
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return Response({
                "message": "Login exitoso",
                "username": user.username,
                "role": user.role,
                "email": user.email,
                "address": user.address,

            }, status=status.HTTP_200_OK)
        return Response({"error": "Credenciales inválidas"}, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"message": "Logout exitoso"}, status=status.HTTP_200_OK)