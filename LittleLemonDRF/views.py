import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group

from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from djoser.serializers import UserSerializer
from rest_framework import generics, permissions, status
from rest_framework.decorators import permission_classes
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import MenuItem, Category, Cart, Order, OrderItem
from .serializers import MenuItemSerializer, CategorySerializer, ManagerSerializer, DeliveryCrewSerializer, \
    UserGroupSerializer, UserCartSerializer, OrderSerializer, OrderItemSerializer


class OnlyAdminCanEdit(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.is_staff:
            return True
        return request.user.is_authenticated and request.method == 'GET'


class IsManager(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.groups.filter(name='Manager'):
            return True
        return request.user.is_authenticated and (request.user.groups.filter(
            name='Customer') or request.user.groups.filter(
            name='DeliveryCrew')) and request.method == 'GET'


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
    permission_classes = [OnlyAdminCanEdit]


class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsAllowUseEditMethods]


class MenuItemsView(generics.ListCreateAPIView):
    serializer_class = MenuItemSerializer
    ordering_fields = ['price', 'inventory']
    filterset_fields = ['price', 'inventory']
    search_fields = ['title']
    permission_classes = [IsAllowUseEditMethods]

    def get_queryset(self):
        if self.request.query_params.get('category'):
            return MenuItem.objects.filter(category__title=self.request.query_params.get('category'))
        if self.request.query_params.get('price'):
            return MenuItem.objects.filter(price=self.request.query_params.get('price'))
        if self.request.query_params.get('search'):
            return MenuItem.objects.filter(title__contains=self.request.query_params.get('search'))
        return MenuItem.objects.all()


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


class AddOrRemoveFromGroupView(APIView):
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


class UserCartView(APIView):

    def get(self, request):
        user = request.user

        if Cart.objects.filter(user=user).exists():
            cart = Cart.objects.get(user=user)
        else:
            cart = Cart.objects.create(user=user, price=0.00, unit_price=0.00)
            cart.save()
        serializer = UserCartSerializer(cart)
        return JsonResponse(serializer.data, safe=False)

    def post(self, request):

        user = request.user
        if Cart.objects.filter(user=user).exists():
            cart = Cart.objects.get(user=user)
        else:
            cart = Cart.objects.create(user=user, price=0.00, unit_price=0.00)
            cart.save()
        data = JSONParser().parse(request)
        if data['menuitems']:
            for item in data['menuitems']:
                cart.menuitem = MenuItem.objects.get(pk=item['id'])
                cart.save()
        serializer = UserCartSerializer(cart)
        return JsonResponse(serializer.data, safe=False)

    def delete(self, request):
        user = request.user
        if Cart.objects.filter(user=user).exists():
            cart = Cart.objects.get(user=user)
            cart.delete()
        else:
            cart = Cart.objects.create(user=user, price=0.00, unit_price=0.00)
            cart.save()
        data = JSONParser().parse(request)

        serializer = UserCartSerializer(cart)
        return JsonResponse(serializer.data, safe=False)


class SingleOrderView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        if self.request.user.groups.filter(name='DeliveryCrew') or self.request.user.groups.filter(name='DeliveryCrew'):
            queryset = Order.objects.all()
        else:
            queryset = Order.objects.filter(user=self.request.user, pk=self.kwargs['pk'])

        return queryset

    def put(self, request, *args, **kwargs):
        order = self.get_object()
        if order.delivery_crew != None and order.status:
            return JsonResponse({"status": "the order has been delivered"}, status=status.HTTP_200_OK)
        else:
            return JsonResponse({"status": "the order is out for delivery"}, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        if self.request.user.groups.filter(name='DeliveryCrew'):
            order = self.get_object()
            order.status = 1
            order.save()

        return self.put(self, request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        if self.request.user.groups.filter(name='Manager'):
            order = self.get_object()
            order.delete()
            return JsonResponse({"detail": "order deleted"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return JsonResponse({"detail": "403 - forbiden"}, status=status.HTTP_403_FORBIDDEN)


class OrderView(APIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        if self.request.user.groups.filter(name='Manager'):
            if self.request.query_params.get('status'):
                if self.request.query_params.get('status') == "delivered":
                    return Order.objects.filter(status=1)
                else:
                    return Order.objects.filter(status=0)
            return Order.objects.all()
        elif self.request.user.groups.filter(name='DeliveryCrew'):
            if self.request.query_params.get('status'):
                if self.request.query_params.get('status') == "delivered":
                    return Order.objects.filter(delivery_crew=self.request.user, status=1)
                else:
                    return Order.objects.filter(delivery_crew=self.request.user, status=0)
            return Order.objects.filter(delivery_crew=self.request.user)
        else:
            return Order.objects.filter(user=self.request.user)


    def get(self, request, *args, **kwargs):
        user = request.user
        serializer = OrderSerializer(self.get_queryset(), many=True)
        serializer_data = serializer.data

        return JsonResponse(serializer_data, safe=False)


    def post(self, request):
        user = request.user
        try:
            cart = Cart.objects.get(user=user)
            order = Order.objects.create(user=user, total=cart.price, date=datetime.datetime.now().date())
            order.save()
            order_item = OrderItem.objects.create(order=order, menuitem=cart.menuitem, quantity=1,
                                                  unit_price=cart.menuitem.price,
                                                  price=cart.price)
            order_item.save()
            cart.menuitem = None
            cart.save()
            serializer = OrderSerializer(order)

            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
        except Cart.DoesNotExist:
            return JsonResponse({'Detail': 'Bad Request'}, status=status.HTTP_400_BAD_REQUEST)
