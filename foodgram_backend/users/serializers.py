from app.models import Recipe
from rest_framework import serializers
from users.models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField('user_subscribed')

    def user_subscribed(self, author):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            if request.user.is_authenticated:
                user = request.user
        return author.is_subscribed(user)

    class Meta:
        fields = ('id', 'first_name', 'last_name',
                  'username', 'email', 'is_subscribed')

        model = CustomUser


class RecipeCommonSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time')
        model = Recipe


class SubscribedUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField('user_subscribed')
    recipes_count = serializers.SerializerMethodField('get_recipes_count')
    recipes = RecipeCommonSerializer(many=True)

    def user_subscribed(self, author):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            if request.user.is_authenticated:
                user = request.user
        return author.is_subscribed(user)

    def get_recipes_count(self, author):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            if request.user.is_authenticated:
                user = request.user
        return author.recipes_count(user)

    class Meta:
        fields = ('id', 'first_name', 'last_name',
                  'username', 'email', 'is_subscribed',
                  'recipes', 'recipes_count')
        model = CustomUser


class PasswordChangeSerializer(serializers.Serializer):
    new_password = serializers.CharField(style={"input_type": "password"})
    current_password = serializers.CharField(style={"input_type": "password"})
