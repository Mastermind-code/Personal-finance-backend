from datetime import date

import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

from api.models import Category, Transaction

User = get_user_model()

@pytest.mark.django_db
def test_category_spending_summary_current_month():
    user = User.objects.create_user(
        username="john",
        password="qwerty"
    )

    food = Category.objects.create(user=user, name="food")
    transport = Category.objects.create(user=user, name="transport")

    Transaction.objects.create(
        category=food,
        user=user,
        amount=50,
        type="expenditure",
        date=date.today()
    )
    Transaction.objects.create(
        category=food,
        user=user,
        amount=150,
        type="expenditure",
        date=date.today()
    )

    Transaction.objects.create(
        category=transport,
        user=user,
        amount=180,
        type="expenditure",
        date=date.today()
    )

    refresh = RefreshToken.for_user(user)

    client =APIClient()

    client.credentials(
        HTTP_AUTHORIZATION = f"Bearer {refresh.access_token}"
    )

    response = client.get("/api/summary/category/")

    assert response.status_code == 200
    assert len(response.data) == 2


    food_data = next(c for c in response.data if c["category_name"] == "food")
    transport_data = next(c for c in response.data if c["category_name"] == "transport")

    assert food_data["spent"] == 200
    assert transport_data["spent"] == 180


