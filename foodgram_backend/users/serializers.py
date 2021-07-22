from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Follow

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.BooleanField(default=False, read_only=True)

    class Meta:
        fields = ('id', 'first_name', 'last_name',
                  'username', 'email', 'is_subscribed')
        model = User


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('first_name', 'last_name', 'username', 'password', 'email')
        model = User

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class SubscriptionWriteSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'author', 'user')
        model = Follow

    def validate(self, data):
        if data.get('author') == data.get('user'):
            raise ValidationError(
                'Нельзя подписаться на самого себя!'
            )
        if Follow.objects.filter(
            user=data.get('user'),
            author=data.get('author')
        ).exists():
            raise ValidationError(
                'Вы уже подписаны на этого автора!'
            )
        return data


class SubscribedUserSerializer(serializers.ModelSerializer):
    from app.serializers import RecipeCommonSerializer
    recipes_count = serializers.IntegerField(default=0)
    recipes = RecipeCommonSerializer(many=True)

    class Meta:
        fields = ('id', 'first_name', 'last_name',
                  'username', 'email', 'recipes', 'recipes_count')
        model = User


class PasswordChangeSerializer(serializers.Serializer):
    new_password = serializers.CharField(style={'input_type': 'password'})
    current_password = serializers.CharField(style={'input_type': 'password'})

    def validate(self, data):
        if not self.context['request'].user.check_password(data.get(
            'current_password'
        )):
            raise ValidationError(
                'Введенный пароль неправильный!'
            )
        return data
