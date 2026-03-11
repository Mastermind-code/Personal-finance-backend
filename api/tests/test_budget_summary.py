import pytest
from datetime import date
from decimal import Decimal
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from api.models import Category, Budget, Transaction


User = get_user_model()


@pytest.mark.django_db
def test_budget_summary_returns_correct_data():
    user = User.objects.create_user(username="john", password="pass")

    refresh = RefreshToken.for_user(user)

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    category = Category.objects.create(user=user, name="Food")

    Budget.objects.create(
        user=user,
        category=category,
        amount=Decimal("100.00"),
        period="monthly"
    )

    Transaction.objects.create(
        user=user,
        category=category,
        amount=Decimal("40.00"),
        type="expenditure"
    )

    response = client.get("/api/budgets/summary/")

    assert response.status_code == 200

    data = response.data[0]

    assert data["category_name"] == "Food"
    assert Decimal(data["budget"]) == Decimal("100.00")
    assert Decimal(data["spent"]) == Decimal("40.00")
    assert Decimal(data["remaining"]) == Decimal("60.00")
    assert data["is_over_budget"] is False
    assert data["percentage_used"] == 40.0