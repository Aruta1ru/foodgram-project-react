from django.http import request
from rest_framework import serializers

from .models import CustomUser, Follow


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField('user_subscribed')

    def user_subscribed(self, author):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user     
        return author.is_subscribed(user)

    class Meta:
        fields = ('id', 'first_name', 'last_name',
                  'username', 'email', 'is_subscribed')

        model = CustomUser


class PasswordChangeSerializer(serializers.Serializer):
    new_password = serializers.CharField(style={"input_type": "password"})
    current_password = serializers.CharField(style={"input_type": "password"})
