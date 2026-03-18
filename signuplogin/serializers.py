from rest_framework import serializers
from django.contrib.auth.models import User

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def validate_username(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Username too short!")
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value

    def validate_password(self, value):
        if len(value) < 4:
            raise serializers.ValidationError("Password too short!")
        special_chars = ['!', '@', '#', '$', '%', '^', '&', '*']
        if not any(char in value for char in special_chars):
            raise serializers.ValidationError("Password must contain at least one special character")
        return value

    def validate_email(self, value):

        allowed_domains = ["gmail.com"]

        domain = value.split("@")[-1].lower()

        if domain not in allowed_domains:
            raise serializers.ValidationError("Only gmail.com emails allowed")

        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")

        return value
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)