import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

from api.models import Category

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

