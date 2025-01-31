from rest_framework import generics
from .models import UserProfile, FriendRequest, Friendship
from .serializers import UserProfileSerializer, FriendRequestSerializer, FriendshipSerializer
from rest_framework.permissions import IsAuthenticated

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required

import requests
from django.shortcuts import redirect
from django.conf import settings
from urllib.parse import urlencode
from django.shortcuts import get_object_or_404
from .forms import UsernameChangeForm



class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.profile
    
class FriendRequestListCreateView(generics.ListCreateAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return FriendRequest.objects.filter(to_user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(from_user=self.request.user)

class FriendshipListView(generics.ListAPIView):
    serializer_class = FriendshipSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Friendship.objects.filter(user1=self.request.user) | Friendship.objects.filter(user2=self.request.user)

def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "You have successfully logged in!")
            return redirect('/')  # Redirect to the homepage or dashboard
        else:
            messages.error(request, "Invalid username or password")
    return render(request, 'profiles/login.html')

def register_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('/register/')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already in use, please try another.")
            return redirect('/register/')

        user = User.objects.create_user(username=username, password=password)
        messages.success(request, "Registration successful! Please log in.")
        return redirect('/')
    return render(request, "profiles/register.html")

def home_view(request):
    if request.user.is_authenticated:
        return render(request, "profiles/home.html")  # Render homepage for logged-in users
    else:
        return redirect('/login/')  # Redirect non-logged-in users to login
    

def welcome_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/dashboard/')
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, "profiles/welcome.html")

@login_required
def dashboard_view(request):
    access_token = request.session.get('spotify_access_token')

    if not access_token:
        # If the user is not connected to Spotify, prompt them to log in
        return render(request, "profiles/dashboard.html", {
            "top_artists": [],
            "time_range": None,
            "prompt_spotify_login": True,
            "username": request.user.username,  # Pass the logged-in user's username
        })

    time_range = request.GET.get('time_range', 'medium_term')  # Default to medium_term

    # Fetch top artists from Spotify API
    url = "https://api.spotify.com/v1/me/top/artists"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"time_range": time_range, "limit": 50}

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        top_artists = response.json().get('items', [])
    else:
        top_artists = []
        print(f"Spotify API Error: {response.status_code}, {response.json()}")

    # Render the dashboard with the username and top artists
    return render(request, "profiles/dashboard.html", {
        "top_artists": top_artists,
        "time_range": time_range,
        "username": request.user.username,  # Pass the logged-in user's username
    })


def logout_view(request):
    logout(request)  # End the user session
    return redirect('/')  # Redirect to the welcome/login page

def spotify_login(request):
    scopes = "user-top-read"
    params = {
        "client_id": settings.SPOTIFY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
        "scope": scopes,
    }
    url = f"https://accounts.spotify.com/authorize?{urlencode(params)}"
    return redirect(url)

def spotify_callback(request):
    code = request.GET.get("code")
    if not code:
        return redirect("/")  # Redirect to the login page if no code

    # Exchange code for access token
    token_url = "https://accounts.spotify.com/api/token"
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
        "client_id": settings.SPOTIFY_CLIENT_ID,
        "client_secret": settings.SPOTIFY_CLIENT_SECRET,
    }
    response = requests.post(token_url, data=data)
    response_data = response.json()

    access_token = response_data.get("access_token")
    if not access_token:
        return redirect("/")  # Redirect back if token exchange fails

    # Fetch Spotify user info
    user_info_url = "https://api.spotify.com/v1/me"
    headers = {"Authorization": f"Bearer {access_token}"}
    user_info_response = requests.get(user_info_url, headers=headers)
    user_info = user_info_response.json()

    email = user_info.get("email")
    username = user_info.get("id")

    # Create or get a Django user
    user, created = User.objects.get_or_create(username=username, defaults={"email": email})
    login(request, user)  # Log the user into Django

    # Save Spotify token to session
    request.session['spotify_access_token'] = access_token

    return redirect("/dashboard/")  # Redirect to the dashboard

def public_profile_view(request, username):
    # Get the user by username or raise a 404 with a custom message
    user = get_object_or_404(User, username=username)

    # For testing, fetch top artists directly from Spotify API
    # In production, this should be cached or stored in a database to avoid rate limits
    access_token = request.session.get('spotify_access_token')  # Temporary: Use session for now

    if not access_token:
        # If no access token is found, return an empty artist list
        top_artists = []
    else:
        # Fetch top artists from Spotify API
        url = "https://api.spotify.com/v1/me/top/artists"
        headers = {"Authorization": f"Bearer {access_token}"}
        params = {"time_range": "medium_term", "limit": 50}

        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            top_artists = response.json().get('items', [])
        else:
            top_artists = []
            print(f"Spotify API Error: {response.status_code}, {response.json()}")

    # Render the public profile template
    return render(request, "profiles/public_profile.html", {
        "profile_user": user,  # The user being viewed
        "top_artists": top_artists,  # List of top artists
    })

@login_required
def change_username_view(request):
    profile = request.user.profile

    if request.method == "POST":
        form = UsernameChangeForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your username has been updated successfully!")
            return redirect('dashboard')  # Redirect to the dashboard or another page
    else:
        form = UsernameChangeForm(instance=profile)

    return render(request, 'profiles/change_username.html', {'form': form})