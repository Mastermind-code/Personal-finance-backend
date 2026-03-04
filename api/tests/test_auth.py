import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()
@pytest.mark.django_db
def test_user_can_register():
    client = APIClient()
    response = client.post(
        '/api/auth/register/',
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
        '/api/auth/login/',
        {
            'username': 'john',
            'password': 'strongpassword123'
        },
        format='json'
    )
    assert response.status_code ==200
    assert 'access' in response.data


@pytest.mark.django_db

def test_authenticated_user_can_access_profile_endpoint():
    user = User.objects.create_user(
        username="john",
        password='password',
        email='johndoe@example.com'
    )
    refresh = RefreshToken.for_user(user)

    client = APIClient()

    client.credentials(
        HTTP_AUTHORIZATION= f'Bearer {refresh.access_token}'
    )

    response = client.get("/api/auth/profile/")

    assert response.status_code == 200
    assert response.data['username'] == "john"
    assert response.data['email'] =='johndoe@example.com'


@pytest.mark.django_db
def test_unauthorized_user_cannot_access_profile_endpoint():
    client = APIClient()
    response = client.get('/api/auth/profile/')

    assert response.status_code == 401
