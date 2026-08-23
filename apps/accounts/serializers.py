"""
Serializers for accounts application.
"""
from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """
    Public / Staff safe serializer for User model.
    """
    role_display = serializers.CharField(source="get_role_display", read_only=True)
    full_name = serializers.CharField(source="get_full_name", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "role",
            "role_display",
            "title",
            "department",
            "avatar",
            "bio",
            "is_staff_member",
            "date_joined",
        ]
        read_only_fields = ["id", "date_joined", "role", "role_display", "is_staff_member"]
