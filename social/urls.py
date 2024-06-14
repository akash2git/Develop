from django.urls import path
from . import views

urlpatterns = [
    path('register', views.register, name='register'),
    path('login', views.login, name='login'),
    path('search_user', views.search_user, name='search_user'),
    path('send_friend_request', views.send_friend_request, name='send_friend_request'),
    path('accept_friend_request', views.accept_friend_request, name='accept_friend_request'),
    path('reject_friend_request', views.reject_friend_request, name='reject_friend_request'),
    path('list_friends', views.list_friends, name='list_friends'),
    path('list_pending_requests', views.list_pending_requests, name='list_pending_requests'),
    path('logout', views.logout, name='logout'),
]
