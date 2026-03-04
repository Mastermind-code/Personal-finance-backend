from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView
from api.views import RegisterView, ProfileView, CategoryViewSet, BudgetViewSet, TransactionViewSet, CategorySpendingSummaryView
from rest_framework.routers import DefaultRouter




router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="category"),
router.register(r"budgets", BudgetViewSet, basename="budget"),
router.register(r"transactions", TransactionViewSet, basename="transaction"),

urlpatterns = [
path('auth/register/', RegisterView.as_view()),
    path('auth/login/', TokenObtainPairView.as_view()),
    path('auth/profile/', ProfileView.as_view()),
    path('summary/category/', CategorySpendingSummaryView.as_view()),
]

urlpatterns+=router.urls    