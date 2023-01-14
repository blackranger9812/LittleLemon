from django.urls import path, include, re_path
from rest_framework.authtoken.views import obtain_auth_token

from restaurant.views import *
from restaurant.views import BookingView

urlpatterns = [
    re_path(r'^auth/', include('djoser.urls')),
    path('api-token-auth/', obtain_auth_token),
    path('menu/', MenuView.as_view()),
    path('menu/<int:pk>', SingleMenuItemView.as_view()),
    path('booking/', BookingView.as_view(), name='menu'),
]
