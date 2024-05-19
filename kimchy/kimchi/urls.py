from django.urls import path
from . import views

urlpatterns = [
    path('', views.register, name='register'),
    path('login', views.login, name='login'),
    path('success', views.success, name='success'),
    path('place_order', views.place_order, name='place_order'),
    path('orders_list', views.orders, name='orders_list'),
    path('logout', views.logout, name='logout'),
]
