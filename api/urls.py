from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView
from api.views import RegisterView, ProfileView, CategoryViewSet
from rest_framework.routers import DefaultRouter




router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="category")

urlpatterns = [
path('auth/register/', RegisterView.as_view()),
    path('auth/login/', TokenObtainPairView.as_view()),
    path('auth/profile/', ProfileView.as_view()),
]

urlpatterns+=router.urls