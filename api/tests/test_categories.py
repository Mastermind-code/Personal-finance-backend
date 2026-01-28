import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
@pytest.mark.django_db
def test_authenticated_user_can_create_categories():
    user = User.objects.create_user(
        username= 'john doe',
        password="johndoe@example.com"
    )

    refresh = RefreshToken.for_user(user)

    client = APIClient()
    client.credentials(
        HTTP_AUTHORIZATION=f"bearer{refresh.access_token} "
    )

    response = client.post(
        "/api/categories/",
        {"name": 'Food'},
        format="json"

    )

    assert response.status_code == 201
    assert response.data["name"] == "Food"