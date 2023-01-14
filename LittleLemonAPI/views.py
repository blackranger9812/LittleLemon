from django.shortcuts import render

# Create your views here.
from djoser.conf import User
from djoser.serializers import UserSerializer
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from LittleLemonAPI.models import MenuItem, booking, menu
from LittleLemonAPI.serializers import MenuItemSerializer, BookingSerializer, MenuSerializer


class MenuItemsView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer


class SingleMenuItemView(generics.RetrieveUpdateAPIView, generics.DestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer


class BookingView(APIView):
    def get(self, request):
        items = booking.objects.all()
        serializer = BookingSerializer(items, many=True)
        return Response(serializer.data)


class MenuView(generics.ListCreateAPIView):
    queryset = menu.objects.all()
    serializer_class = MenuSerializer
    permission_classes = [IsAuthenticated]


class BookingViewSet(ModelViewSet):
    queryset = booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
