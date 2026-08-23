"""
Views for user authentication and account management.
"""
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
    PasswordChangeView,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import View, UpdateView
from rest_framework import generics, permissions
from .forms import CustomLoginForm, UserProfileUpdateForm
from .models import User
from .serializers import UserSerializer


class CustomLoginView(View):
    """
    Custom login view with enhanced styling and redirect awareness.
    """
    template_name = "accounts/login.html"
    form_class = CustomLoginForm

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_staff_member:
                return redirect("dashboard:index")
            return redirect("website:home")
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            # Capture client IP
            x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
            if x_forwarded_for:
                ip = x_forwarded_for.split(",")[0]
            else:
                ip = request.META.get("REMOTE_ADDR")
            user.last_login_ip = ip
            user.save(update_fields=["last_login_ip"])
            
            # Handle remember me session duration
            remember_me = form.cleaned_data.get("remember_me")
            if not remember_me:
                request.session.set_expiry(0)  # Browser close
            else:
                request.session.set_expiry(1209600)  # 2 weeks
                
            auth_login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}.")
            
            next_url = request.GET.get("next")
            if next_url:
                return redirect(next_url)
            if user.is_staff_member:
                return redirect("dashboard:index")
            return redirect("website:home")
        
        messages.error(request, "Invalid username or password. Please try again.")
        return render(request, self.template_name, {"form": form})


class CustomLogoutView(View):
    """
    Logout view that safely terminates session and redirects.
    """
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            auth_logout(request)
            messages.info(request, "You have been signed out successfully.")
        return redirect("website:home")


class ProfileView(LoginRequiredMixin, UpdateView):
    """
    User account profile editing view.
    """
    model = User
    form_class = UserProfileUpdateForm
    template_name = "accounts/profile.html"
    success_url = reverse_lazy("accounts:profile")

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Your profile has been updated successfully.")
        return super().form_valid(form)


# ==============================================================================
# REST API VIEWS
# ==============================================================================

class CurrentUserApiView(generics.RetrieveAPIView):
    """
    API endpoint to retrieve the currently logged in user profile.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
