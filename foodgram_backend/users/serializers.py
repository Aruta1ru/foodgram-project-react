from app.serializers import RecipeCommonSerializer
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from rest_framework.fields import HiddenField, CurrentUserDefault
from rest_framework import serializers

from .models import Follow

user = get_user_model()


def validate_author(data):
    if data.get('author') == data.get('user'):
        raise ValidationError(
            'Нельзя подписаться на самого себя!'
        )
    return data


def follow_already_exists(data):
    if Follow.objects.filter(
        user=data.get('user'),
        author=data.get('author')
    ).exists():
        raise ValidationError(
            'Вы уже подписаны на этого автора!'
        )


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField('user_subscribed')

    def user_subscribed(self, author):
        user = None
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            if request.user.is_authenticated:
                user = request.user
        return author.annotate_subscribed_flag(user)

    class Meta:
        fields = ('id', 'first_name', 'last_name',
                  'username', 'email', 'is_subscribed')

        model = user


class SubscriptionSerializer(serializers.ModelSerializer):
    user = HiddenField(default=CurrentUserDefault())

    class Meta:
        fields = ('author', 'user')
        model = Follow
        validators = (validate_author, follow_already_exists)


class SubscribedUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField('user_subscribed')
    recipes_count = serializers.SerializerMethodField('get_recipes_count')
    recipes = RecipeCommonSerializer(many=True)

    def user_subscribed(self, author):
        user = None
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            if request.user.is_authenticated:
                user = request.user
        return author.is_subscribed(user)

    def get_recipes_count(self, author):
        user = None
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            if request.user.is_authenticated:
                user = request.user
        return author.annotate_recipes_count(user)

    class Meta:
        fields = ('id', 'first_name', 'last_name',
                  'username', 'email', 'is_subscribed',
                  'recipes', 'recipes_count')
        model = user


class PasswordChangeSerializer(serializers.Serializer):
    new_password = serializers.CharField(style={'input_type': 'password'})
    current_password = serializers.CharField(style={'input_type': 'password'})
