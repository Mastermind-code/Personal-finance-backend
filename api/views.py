from datetime import date

from django.db.models import Sum, Q
from django.shortcuts import render
from rest_framework import generics, permissions
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from .models import Category, Budget, Transaction
from api.serializers import RegisterSerializer, UserSerializer, CategorySerializer, BudgetSerializer, \
    TransactionSerializer


# Create your views here.
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]



class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class CategoryViewSet(ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)


class BudgetViewSet(ModelViewSet):
    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        today = date.today()
        month_start = today.replace(day=1)
        return Budget.objects.filter(user=self.request.user).annotate(
            spent=Sum(
                "category__transaction__amount",
                filter=Q(
                    category__transaction__type=Transaction.EXPENDITURE,
                    category__transactions__date__gte=month_start,
                    category__transactions__date__lte=today,
                )
            )
        )



class TransactionViewSet(ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)



class CategorySpendingSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = date.today()
        month = today.replace(day=1)
        summary = Transaction.objects.filter(
            user=request.user,
            type=Transaction.EXPENDITURE,
            date__gte=month,
            date__lte=today
        ).values(
            "category__name",
            "category__id"
        ).annotate(
            spent=Sum(
                "amount",
                filter=Q(
                    type=Transaction.EXPENDITURE,
                    date__gte=month,
                    date__lte=today
                )
            )
        ).order_by(
            "category__name"
        )
        return Response([
            {
                "category_name": item['category__name'],
                "category_id": item['category__id'],
                "spent": item['spent']
            }
            for item in summary
        ])

