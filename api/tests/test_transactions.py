import pytest
from datetime import date
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

from api.models import Category, Budget, Transaction

User = get_user_model()

@pytest.mark.django_db
def test_use_can_create_transactions():
    user = User.objects.create_user(
        username="john",
        password="qwerty"
    )

    category = Category.objects.create(
        name="food",
        user=user
    )

    refresh = RefreshToken.for_user(user)

    client = APIClient()
    client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}",
    )
    response = client.post(
        "/api/transactions/",
        {
            'category': category.id,
            'amount': '50.00',
            'type': 'income',
            'description': "Lunch"
        },
        format = "json"
    )
    print(response.data)

    assert response.status_code == 201
    assert response.data["amount"] == '50.00'
    assert response.data['type'] == 'income'


@pytest.mark.django_db
def test_user_cannot_create_transactions_with_other_users_category():
    user1 = User.objects.create_user(
        username="john",
        password = "qwerty"
    )
    user2 = User.objects.create_user(
        username="doe",
        password="pouyt"
    )

    category2 = Category.objects.create(user=user2, name="food")

    refresh = RefreshToken.for_user(user1)

    client = APIClient()
    client.credentials(
        HTTP_AUTHORIZATION= f"Bearer {refresh.access_token}"
    )

    response = client.post(
        "/api/transactions/",
        {
            "category": category2.id,
            "amount": "50.00",
            "type": "expenditure",
            "description": "lunch"
        },
        format="json"
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_transaction_over_budget_detection():
    user = User.objects.create_user(
        username="john",
        password="qwerty"
    )

    category = Category.objects.create(user=user, name="food")

    Budget.objects.create(
        user=user,
        category=category,
        amount=100,
        period="monthly"
    )
    Transaction.objects.create(
        user=user,
        category=category,
        amount=50,
        type="expenditure",
        date=date.today()
    )

    refresh = RefreshToken.for_user(user)
    client = APIClient()
    client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}",
    )

    response = client.post(
        "/api/transactions/",
        {
            "category": category.id,
            "amount": "150.00",
            "type": "expenditure",
            "description": "Dinner"
        },
        format="json"
    )

    assert response.status_code == 201
    assert response.data["is_over_budget"] is True
    assert response.data["remaining_budget"] == -100.00


@pytest.mark.django_db
def test_transaction_remaining_budget_calculation():
    user = User.objects.create_user(
        username="john",
        password="qwerty"
    )

    category = Category.objects.create(user=user, name="food")

    Budget.objects.create(
        user=user,
        category=category,
        amount=100,
        period="monthly"
    )
    
    
    refresh = RefreshToken.for_user(user)
    client = APIClient()
    client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}",
    )
    response1 = client.post(
        "/api/transactions/",
        {
            "category": category.id,
            "amount": "50.00",
            "type": "expenditure",
            "description": "Lunch"
        },
        format="json"
    )
    assert response1.data["remaining_budget"] == 50.00
    assert response1.status_code == 201             
    assert response1.data["is_over_budget"] is False

    response2 = client.post(
        "/api/transactions/",
        {
            "category": category.id,
            "amount": "150.00",
            "type": "expenditure",
            "description": "Dinner"
        },
        format="json"
    )

    assert response2.status_code == 201
    assert response2.data["is_over_budget"] is True
    assert response2.data["remaining_budget"] == -100.00