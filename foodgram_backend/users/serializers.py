from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CurrentUserDefault, HiddenField
from rest_framework.relations import PrimaryKeyRelatedField

from .models import Follow

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField('user_subscribed')

    def user_subscribed(self, author):
        user = None
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            if request.user.is_authenticated:
                user = request.user
        return User.objects.annotate_subscribed_flag(
            user, author
        ).get(id=author.id).is_subscribed

    class Meta:
        fields = ('id', 'first_name', 'last_name',
                  'username', 'email', 'is_subscribed')

        model = User


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
    is_subscribed = serializers.SerializerMethodField('user_subscribed')
    recipes_count = serializers.SerializerMethodField('get_recipes_count')
    recipes = RecipeCommonSerializer(many=True)

    def user_subscribed(self, author):
        user = None
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            if request.user.is_authenticated:
                user = request.user
        return User.objects.annotate_subscribed_flag(
            user, author
        ).get(id=author.id).is_subscribed

    def get_recipes_count(self):
        user = None
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            if request.user.is_authenticated:
                user = request.user
        return User.objects.annotate_recipes_count(
            user
        ).get(id=user.id).recipes_count

    class Meta:
        fields = ('id', 'first_name', 'last_name',
                  'username', 'email', 'is_subscribed',
                  'recipes', 'recipes_count')
        model = User


class PasswordChangeSerializer(serializers.Serializer):
    new_password = serializers.CharField(style={'input_type': 'password'})
    current_password = serializers.CharField(style={'input_type': 'password'})
