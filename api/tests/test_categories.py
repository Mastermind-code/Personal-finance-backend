import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from api.models import Category

@pytest.mark.django_db
def test_authenticated_user_can_create_categories():
    user = User.objects.create_user(
        username= 'john doe',
        password="johndoe@example.com"
    )

    refresh = RefreshToken.for_user(user)

    client = APIClient()
    client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}"
    )

    response = client.post(
        "/api/categories/",
        {"name": 'Food'},
        format="json"

    )

    assert response.status_code == 201
    assert response.data["name"] == "Food"

def test_user_can_only_see_their_own_category():
    user1 = User.objects.create_user(
        username='james bond',
        password='poiuy'
    )

    user2 = User.objects.create_user(
        username="john doe",
        password='123qwerty'
    )

    Category.objects.create(name="food", user=user1)
    Category.objects.create(name='sport', user=user2)

    refresh= RefreshToken.for_user(user1)

