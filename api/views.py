from django.shortcuts import render
from rest_framework import generics, permissions
from django.contrib.auth.models import User

from api.serializers import RegisterSerializer


# Create your views here.
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]