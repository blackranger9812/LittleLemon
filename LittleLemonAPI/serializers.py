from djoser.conf import User
from rest_framework import serializers

from LittleLemonAPI.models import MenuItem, menu, booking


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'inventory']


class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = menu
        fields = '__all__'


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = booking
        fields = '__all__'