from rest_framework.test import APIClient
import pytest
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken


from api.models import Category


@pytest.mark.django_db
def test_user_can_create_budget():
    user = User.objects.create_user(
        username = "joh doe",
        password = "qwerty"
    )
    category = Category.objects.create(name="food", user=user)

    refresh = RefreshToken.for_user(user)

    client = APIClient()
    client.credentials(
        HTTP_AUTHORIZATION = f"Bearer {refresh.access_token}"
    )

    response = client.post(
        "/api/budgets/",
        {
            "category": category.id,
            'amount': "500.00"
        },
        format="json"
    )

    assert response.status_code == 201
    assert response.data['amount'] == "500.00"

@pytest.mark.django_db
def test_user_cannot_create_duplicate_budget_for_category():
    user = User.objects.create_user(
        username = 'john doe',
        password = "qwerty"
    )
    category = Category.objects.create(name="food", user=user)

    refresh = RefreshToken.for_user(user)

    client = APIClient()
    client.credentials(
        HTTP_AUTHORIZATION = f"Bearer {refresh.access_token}"
    )

    client.post(
        "/api/budgets/",
        {
            "category":category.id,
            "amount": "500.00"
        },
        format = 'json'

    )

    response = client.post(
        "/api/budgets/",
        {
            "category": category.id,
            "name": "300.00"
        },
        format = "json"
    )
    assert response.status_code == 400
