
from rest_framework.request import Request
from django.db.models import DecimalField
from django.db.models.functions import Coalesce
from rest_framework.decorators import permission_classes
from datetime import date
from decimal import Decimal
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
    TransactionSerializer, BudgetSummarySerializer


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
                "category__transactions__amount",
                filter=Q(
                    category__transactions__type=Transaction.EXPENDITURE,
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


class BudgetSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get_date_range(self, period):
        today = date.today()
        if period == 'monthly':
            return today.replace(day=1), today
        # elif period == 'weekly':
        #     start = today - timedelta(days=today.weekday())
        #     return start, today
        # elif period == 'yearly':
        #     return today.replace(month=1, day=1), today
        return None, None

    def get(self, request):
        today = date.today()
        month_start = today.replace(day=1)

        monthly_budgets = Budget.objects.filter(
            user=request.user,
            period='monthly'
        ).annotate(
            spent=Coalesce(
                Sum(
                    'category__transactions__amount',
                    filter=Q(
                        category__transactions__type=Transaction.EXPENDITURE,
                        category__transactions__date__gte=month_start,
                        category__transactions__date__lte=today,
                    )
                ),
                Decimal('0.00'),
                output_field=DecimalField()
            )
        ).select_related('category')

        budgets = list(monthly_budgets)
        # budgets += list(weekly_budgets)   # add later
        # budgets += list(yearly_budgets)   # add later

        data = []
        for budget in budgets:
            remaining = budget.amount - budget.spent
            percentage_used = (
                round(float((budget.spent / budget.amount) * 100), 2)
                if budget.amount
                else 0.0
            )
            data.append({
                'category_id': budget.category.id,
                'category_name': budget.category.name,
                'budget': budget.amount,
                'spent': budget.spent,
                'remaining': remaining,
                'percentage_used': percentage_used,
                'is_over_budget': budget.spent > budget.amount,
            })

        serializer = BudgetSummarySerializer(data, many=True)
        return Response(serializer.data)
            

class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = date.today()
        month_start = today.replace(day=1)

        transactions = Transaction.objects.filter(
            user=request.user,
            date__gte=month_start,
            date__lte=today,
        )

        total_income = transactions.filter(
            type=Transaction.INCOME
        ).aggregate(
            total=Coalesce(Sum('amount'), Decimal('0.00'), output_field=DecimalField())
        )['total']

        total_expenditure = transactions.filter(
            type=Transaction.EXPENDITURE
        ).aggregate(
            total=Coalesce(Sum('amount'), Decimal('0.00'), output_field=DecimalField())
        )['total']

        net_balance = total_income - total_expenditure

        budgets = Budget.objects.filter(
            user=request.user,
            period='monthly'
        ).annotate(
            spent=Coalesce(
                Sum(
                    'category__transactions__amount',
                    filter=Q(
                        category__transactions__type=Transaction.EXPENDITURE,
                        category__transactions__date__gte=month_start,
                        category__transactions__date__lte=today,
                    )
                ),
                Decimal('0.00'),
                output_field=DecimalField()
            )
        )

        total_budget = budgets.aggregate(
            total=Coalesce(Sum('amount'), Decimal('0.00'), output_field=DecimalField())
        )['total']

        total_spent = budgets.aggregate(
            total=Coalesce(Sum('spent'), Decimal('0.00'), output_field=DecimalField())
        )['total']

        total_remaining = total_budget - total_spent
        budgets_over_limit = total_spent > total_budget

        top_category = transactions.filter(
            type=Transaction.EXPENDITURE
        ).values(
            'category__name'
        ).annotate(
            total=Sum('amount')
        ).order_by('-total').first()

        return Response({
            'total_income': total_income,
            'total_expenditure': total_expenditure,
            'net_balance': net_balance,
            'total_budget': total_budget,
            'total_spent': total_spent,
            'total_remaining': total_remaining,
            'budgets_over_limit': budgets_over_limit,
            'top_spending_category': top_category['category__name'] if top_category else None,
            'top_spending_amount': top_category['total'] if top_category else None,
        })