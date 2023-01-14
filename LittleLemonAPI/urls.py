
from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from LittleLemonAPI import views
from LittleLemonAPI.views import BookingView

urlpatterns = [
    path('api-token-auth/', obtain_auth_token),
    path('menu-items/', views.MenuItemsView.as_view()),
    path('menu-items/<int:pk>/', views.SingleMenuItemView.as_view()),
    path('booking/', BookingView.as_view(), name='menu'),
]