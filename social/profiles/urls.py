from django.urls import path
from .views import welcome_view, register_view, dashboard_view, logout_view, spotify_callback, spotify_login, public_profile_view, UserProfileView, FriendRequestListCreateView, FriendshipListView

urlpatterns = [
    path('', welcome_view, name='welcome'),  # Default welcome and login
    path('login/', welcome_view, name='login'),  # Explicit login route
    path('register/', register_view, name='register'),  # Registration page
    path('dashboard/', dashboard_view, name='dashboard'),  # Dashboard page
    path('profile/', UserProfileView.as_view(), name='user-profile'),  # User profile endpoint
    path('friends/requests/', FriendRequestListCreateView.as_view(), name='friend-requests'),  # Friend requests
    path('friends/', FriendshipListView.as_view(), name='friendships'),  # Friendships
    path('logout/', logout_view, name='logout'),  # Logout route
    path('spotify/login/', spotify_login, name='spotify-login'),
    path('spotify/callback/', spotify_callback, name='spotify-callback'),
    path('profile/<str:username>/', public_profile_view, name='public-profile'),
]
