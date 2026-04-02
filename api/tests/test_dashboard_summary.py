from decimal import Decimal
from rest_framework.test import APIClient
from api.models import Transaction
from api.models import Category
from api.models import Budget
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
import pytest


User = get_user_model()

@pytest.mark.django_db
def test_dashboard_summary():
    user = User.objects.create_user(username="john", password="pass")

    refresh = RefreshToken.for_user(user)

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    food = Category.objects.create(user=user, name="Food")
    transport = Category.objects.create(user=user, name='Transport')

    Budget.objects.create(
        user=user,
        category=food,
        amount=Decimal("100.00"),
        period="monthly"
    )
    Budget.objects.create(
        user=user,
        category=transport,
        amount=Decimal("50.00"),
        period="monthly"
    )
    Transaction.objects.create(
        user=user,
        category=food,
        amount=Decimal("40.00"),
        type="expenditure"
    )
    Transaction.objects.create(
        user=user,
        category=food,
        amount=Decimal("200.00"),
        type='income'
    )
    Transaction.objects.create(
        user=user,
        category=transport,
        amount=Decimal("30.00"),
        type="expenditure"
    )

    response = client.get("/api/dashboard/")

    assert response.status_code == 200

    data = response.data

    assert Decimal(data["total_income"]) == Decimal("200.00")
    assert Decimal(data["total_expenditure"]) == Decimal("70.00")
    assert Decimal(data["net_balance"]) == Decimal("130.00")
    assert Decimal(data["total_budget"]) == Decimal("150.00")
    assert Decimal(data["total_spent"]) == Decimal("70.00")
    assert Decimal(data["total_remaining"]) == Decimal("80.00")
    assert data["budgets_over_limit"] is False
    assert data["top_spending_category"] == "Food"
    assert Decimal(data["top_spending_amount"]) == Decimal("40.00")