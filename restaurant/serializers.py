from djoser.conf import User
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from restaurant.models import MenuItem, Booking


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class MenuSerializer(ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['title', 'price', 'inventory']


class BookingSerializer(ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'
