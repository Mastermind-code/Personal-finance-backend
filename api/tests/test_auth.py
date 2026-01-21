import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User

@pytest.mark.django_db
def test_user_can_register():
    client = APIClient()
    response = client.post(
        'api/auth/register',
        {
            'username': 'john',
            'password': 'strongpassword123',
            'email': 'johndoe@gmail.com'
        },
        format='json'
    )
    assert response.status_code == 201
    assert User.objects.filter(username="john").exists()

@pytest.mark.django_db
def test_user_can_login_and_receive_token():
    User.objects.create_user(
        username="john",
        password="strongpassword123"
    )
    client = APIClient()
    response = client.post(
        'api/auth/login',
        {
            'username': 'john',
            'password': 'strongpassword123'
        },
        format='json'
    )
    assert response.status_code ==200
    assert 'access' in response.data


