from django.contrib.auth.models import User
from rest_framework import generics, permissions
from rest_framework.permissions import IsAdminUser

from .models import MenuItem, Category
from .serializers import MenuItemSerializer, CategorySerializer, ManagerSerializer, DeliveryCrewSerializer


class IsManager(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.groups.filter(name='Manager')


class IsAllowUseEditMethods(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.groups.filter(name='Manager'):
            return True
        return request.user.is_authenticated and (request.user.groups.filter(
            name='Customer') or request.user.groups.filter(
            name='DeliveryCrew')) and request.method == 'GET'


class CategoriesView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsAllowUseEditMethods]


class MenuItemsView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    ordering_fields = ['price', 'inventory']
    filterset_fields = ['price', 'inventory']
    search_fields = ['title']
    permission_classes = [IsAllowUseEditMethods]


class SingleManagerView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.filter(groups__name__contains='Manager')
    serializer_class = ManagerSerializer
    permission_classes = [IsManager]


class ManagersView(generics.ListCreateAPIView):
    queryset = User.objects.filter(groups__name__contains='Manager')
    serializer_class = ManagerSerializer
    permission_classes = [IsManager]


class SingleDeliveryCrewView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.filter(groups__name__contains='DeliveryCrew')
    serializer_class = DeliveryCrewSerializer
    permission_classes = [IsManager]


class DeliveryCrewsView(generics.ListCreateAPIView):
    queryset = User.objects.filter(groups__name__contains='DeliveryCrew')
    serializer_class = DeliveryCrewSerializer
    permission_classes = [IsManager]
