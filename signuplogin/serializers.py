

from rest_framework import serializers
from .models import Signup


class SignupSerializer(serializers.ModelSerializer):

    class Meta:
        model = Signup
        fields = ["username", "email", "password"]

    def validate_username(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Username too short!")
        return value

    def validate_password(self, value):
        if len(value) < 4:
            raise serializers.ValidationError("Password too short!")
        return value
