import base64
import uuid

from app.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                        RecipeTag, ShoppingCart, Tag)
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db import transaction
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from rest_framework.validators import UniqueTogetherValidator

from users.serializers import UserSerializer

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            id = uuid.uuid4()
            data = ContentFile(base64.b64decode(imgstr),
                               name=id.urn[9:] + '.' + ext)
        return super(Base64ImageField, self).to_internal_value(data)


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = Ingredient


class RecipeIngredientSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(source='ingredient',
                                            read_only=True)
    name = serializers.StringRelatedField(source='ingredient.name', many=False)
    measurement_unit = serializers.StringRelatedField(
        source='ingredient.measurement_unit', many=False
    )
    amount = serializers.IntegerField(read_only=True)

    class Meta:
        fields = ('id', 'name', 'measurement_unit', 'amount')
        model = RecipeIngredient


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = Tag


class RecipeCommonSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time')
        model = Recipe


class RecipeSerializer(serializers.ModelSerializer):
    author = SerializerMethodField('get_recipe_author')
    ingredients = RecipeIngredientSerializer(
        source='recipe_ingredients', many=True
    )
    is_favorited = serializers.BooleanField(default=False, read_only=True)
    is_in_shopping_cart = serializers.BooleanField(
        default=False, read_only=True
    )
    tags = TagSerializer(many=True, read_only=True)
    image = Base64ImageField()

    def get_recipe_author(self, obj):
        request = self.context.get('request')
        author = User.objects.annotate_subscribed_flag(
            request.user
        ).get(id=obj.author.id)
        return UserSerializer(instance=author).data

    def add_recipe_ingredients(self, recipe, ingredients_data):
        recipe_ingredients = (
            RecipeIngredient(
                recipe=recipe,
                ingredient=Ingredient.objects.get(id=ingredient_data['id']),
                amount=ingredient_data['amount']
            ) for ingredient_data in ingredients_data)
        RecipeIngredient.objects.bulk_create(recipe_ingredients)

    def add_recipe_tags(self, recipe, tags_data):
        recipe_tags = (
            RecipeTag(
                recipe=recipe,
                tag=Tag.objects.get(id=tag_id)
            ) for tag_id in tags_data)
        RecipeTag.objects.bulk_create(recipe_tags)

    @transaction.atomic
    def create(self, validated_data):
        request = self.context.get('request')
        ingredients_data = request.data['ingredients']
        for ingredient in ingredients_data:
            if int(ingredient['amount']) < 0:
                raise serializers.ValidationError(
                    'Количество должно быть больше или равно 0!'
                )
        tags_data = request.data['tags']
        validated_data.pop('recipe_ingredients')
        recipe = Recipe.objects.create(**validated_data)
        self.add_recipe_ingredients(recipe, ingredients_data)
        self.add_recipe_tags(recipe, tags_data)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        request = self.context.get('request')
        ingredients_data = request.data['ingredients']
        for ingredient in ingredients_data:
            if int(ingredient['amount']) < 0:
                raise serializers.ValidationError(
                    'Количество должно быть больше или равно 0!'
                )
        tags_data = request.data['tags']
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time',
                                                   instance.cooking_time)
        instance.image = validated_data.get('image', instance.image)
        instance.save()
        instance.recipe_ingredients.all().delete()
        instance.recipe_tags.all().delete()
        self.add_recipe_ingredients(instance, ingredients_data)
        self.add_recipe_tags(instance, tags_data)
        return instance

    class Meta:
        fields = (
            'id',
            'author',
            'name',
            'text',
            'cooking_time',
            'image',
            'ingredients',
            'tags',
            'is_favorited',
            'is_in_shopping_cart',
        )
        model = Recipe
        depth = 1


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ('id', 'user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=['user', 'recipe'],
                message='Вы уже добавили рецепт в избранное!'
            )
        ]


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = ('id', 'user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=['user', 'recipe'],
                message='Вы уже добавили рецепт в список покупок!')
        ]
