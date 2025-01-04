from rest_framework import generics
from .models import UserProfile, FriendRequest, Friendship
from .serializers import UserProfileSerializer, FriendRequestSerializer, FriendshipSerializer
from rest_framework.permissions import IsAuthenticated

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required


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
    return render(request, "profiles/dashboard.html", {"username": request.user.username})

def logout_view(request):
    logout(request)  # End the user session
    return redirect('/')  # Redirect to the welcome/login page