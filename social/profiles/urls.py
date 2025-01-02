from django.urls import path
from .views import UserProfileView, FriendRequestListCreateView, FriendshipListView, login_view

urlpatterns = [
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('friends/requests/', FriendRequestListCreateView.as_view(), name='friend-requests'),
    path('friends/', FriendshipListView.as_view(), name='friendships'),
    path('login/', login_view, name='login'),
]
