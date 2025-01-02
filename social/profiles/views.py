from rest_framework import generics
from .models import UserProfile, FriendRequest, Friendship
from .serializers import UserProfileSerializer, FriendRequestSerializer, FriendshipSerializer
from rest_framework.permissions import IsAuthenticated

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages


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
            return redirect('/')  # Redirect to the homepage or dashboard
        else:
            messages.error(request, "Invalid username or password")
    return render(request, 'profiles/login.html')