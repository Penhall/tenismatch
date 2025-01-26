# /tenismatch/apps/users/serializers.py 
from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_premium', 'location', 'matches_remaining']
        read_only_fields = ['is_premium', 'matches_remaining']