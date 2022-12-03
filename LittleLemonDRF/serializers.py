from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User, Group
from django.db import models
from django.dispatch import receiver
from rest_framework import serializers
from .models import MenuItem, Category, Cart, Order, OrderItem


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title']


class MenuItemSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(write_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'inventory', 'category', 'category_id']


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('name',)


class UserGroupSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'groups')


class UserCartSerializer(serializers.ModelSerializer):
    menuitem = MenuItemSerializer()

    class Meta:
        model = Cart
        fields = ['id', 'menuitem', 'unit_price', 'price', 'user']


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    items = serializers.RelatedField(source='category', read_only=True)
    class Meta:
        model = Order
        fields = ('id', 'status', 'total', 'date', 'user', 'delivery_crew','items')


class ManagerSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
    )

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data.get('password'))
        user = User.objects.create(**validated_data)
        user.groups.add(Group.objects.get(name='Manager'))
        user.is_staff = True
        user.save()
        return user


class DeliveryCrewSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
    )

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data.get('password'))
        user = User.objects.create(**validated_data)
        user.groups.add(Group.objects.get(name='DeliveryCrew'))
        return user
