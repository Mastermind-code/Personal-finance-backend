from rest_framework.test import APIClient
import pytest
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import date, timedelta

from api.models import Category, Budget, Transaction

User = get_user_model()

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

@pytest.mark.django_dbfi
def test_budget_spent_only_count_current_month_transaction():
    user = User.objects.create_user(
        username="john",
        password="qwerty"
    )
    category = Category.objects.create(user=user, name="food")
    budget = Budget.objects.create(
        category=category,
        user=user,
        amount="500.00",
        period="monthly"
    )
    today = date.today()
    last_month = today.replace(day=1) - timedelta(days=1)

    Transaction.objects.create(
        user=user,
        category=category,
        amount=100,
        type=Transaction.EXPENDITURE,
        date=last_month
    )

    Transaction.objects.create(
        user=user,
        category=category,
        amount=50,
        type= 'expenditure',
        date=today
    )
    refresh = RefreshToken.for_user(user)

    client = APIClient()
    client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}"
    )

    response = client.get(
        "/api/budgets/"
    )
    assert response.status_code == 200
    assert response.data[0]['spent'] == '50.00'
    assert response.data[0]['remaining'] == '450.00'"""
please be consistent irrespective of the bugs we fix. Pasted below is the original next step you suggested. 
However after each bugs you suggest a new one. I need you to be consistent and keep in mind our earlier chats so i wont find learning difficult. 
"""
