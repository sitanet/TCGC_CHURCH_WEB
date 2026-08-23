"""
Forms for authentication and user account management.
"""
from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, UserCreationForm
from django.utils.translation import gettext_lazy as _
from .models import User, UserRole


class CustomLoginForm(AuthenticationForm):
    """
    Styled login form for staff and members.
    """
    username = forms.CharField(
        label=_("Username or Email"),
        widget=forms.TextInput(attrs={
            "class": "form-input",
            "placeholder": "Enter your username or email",
            "autocomplete": "username",
            "autofocus": True,
        })
    )
    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={
            "class": "form-input",
            "placeholder": "Enter your password",
            "autocomplete": "current-password",
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={"class": "form-checkbox"}),
        label=_("Keep me signed in on this device")
    )


class UserProfileUpdateForm(forms.ModelForm):
    """
    Profile update form for users.
    """
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "phone_number", "title", "department", "bio", "avatar"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-input", "placeholder": "First Name"}),
            "last_name": forms.TextInput(attrs={"class": "form-input", "placeholder": "Last Name"}),
            "email": forms.EmailInput(attrs={"class": "form-input", "placeholder": "Email Address"}),
            "phone_number": forms.TextInput(attrs={"class": "form-input", "placeholder": "+234 ..."}),
            "title": forms.TextInput(attrs={"class": "form-input", "placeholder": "e.g. Associate Pastor, Media Lead"}),
            "department": forms.TextInput(attrs={"class": "form-input", "placeholder": "Department or Ministry"}),
            "bio": forms.Textarea(attrs={"class": "form-textarea", "rows": 4, "placeholder": "Brief biographical summary"}),
            "avatar": forms.FileInput(attrs={"class": "form-file-input"}),
        }
