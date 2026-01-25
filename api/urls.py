from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView
from api.views import RegisterView, ProfileView

urlpatterns = [
path('auth/register/', RegisterView.as_view()),
    path('auth/login/', TokenObtainPairView.as_view()),
    path('auth/profile/', ProfileView.as_view()),
]

