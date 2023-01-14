from django.test import TestCase

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from django.urls import reverse

from restaurant.models import MenuItem
from restaurant.serializers import MenuSerializer


class MenuViewTest(TestCase):
    menu_items = [MenuItem(title='potato', price=10, inventory=8),
                  MenuItem(title='flan', price=50, inventory=82),
                  MenuItem(title='mani', price=15, inventory=18),

                  ]

    def setup(self):
        MenuItem.objects.create(title='potato', price=10, inventory=8)
        MenuItem.objects.create(title='flan', price=50, inventory=2)
        MenuItem.objects.create(title='mani', price=15, inventory=18)


    def test_getall(self):
        self.setup()
        User.objects.create_user('user', 'user@user.user', 'testuser')
        user = User.objects.get(username='user')
        user_token, _ = Token.objects.get_or_create(user=user)
        api_client = APIClient()
        api_client.credentials(HTTP_AUTHORIZATION='Token '+user_token.key)
        url = reverse('Restaurant:all_items')
        response = api_client.get(url)
        assert response.status_code == 200
        assert response.data == MenuSerializer(self.menu_items, many=True).data

