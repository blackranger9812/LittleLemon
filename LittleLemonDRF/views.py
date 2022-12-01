from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from djoser.serializers import UserSerializer
from rest_framework import generics, permissions, status
from rest_framework.decorators import permission_classes
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import MenuItem, Category
from .serializers import MenuItemSerializer, CategorySerializer, ManagerSerializer, DeliveryCrewSerializer, \
    UserGroupSerializer


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


"""{
	"groups": [
		{
			"name": "Manager"
		}
	]
}"""


class AddOrRemoveFromGroup(APIView):
    permission_classes = [IsManager]

    def get(self, request, pk):
        try:
            user = User.objects.get(pk=pk)

        except User.DoesNotExist:

            return JsonResponse({"Details": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserGroupSerializer(user)
        return JsonResponse(serializer.data, safe=False)

    def post(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
            data = JSONParser().parse(request)
            if data['groups']:
                for group in data['groups']:
                    user.groups.add(Group.objects.get(name=group['name']))
                    if group['name'] == 'Manager':
                        user.is_staff = True
                        user.save()
                serializer = UserGroupSerializer(user)
                return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)

        except User.DoesNotExist:

            return JsonResponse({"Details": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Group.DoesNotExist:
            return JsonResponse({"Details": "Group does not exist"}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            user = User.objects.get(pk=pk)

        except User.DoesNotExist:

            return JsonResponse({"Details": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        data = JSONParser().parse(request)
        if data['groups']:
            for group in data['groups']:
                user.groups.remove(Group.objects.get(name=group['name']))
                if group['name'] == 'Manager':
                    user.is_staff = False
                    user.save()
            serializer = UserGroupSerializer(user)
            return JsonResponse(serializer.data, status=status.HTTP_200_OK)
