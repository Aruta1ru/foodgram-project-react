import base64
import uuid

from app.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                        RecipeTag, ShoppingCart, Tag)
from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CurrentUserDefault, HiddenField
from users.serializers import UserSerializer


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
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(read_only=True, source='ingredient.name')
    measurement_unit = serializers.CharField(
        read_only=True,
        source='ingredient.measurement_unit'
    )
    amount = serializers.IntegerField(read_only=True)


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'color', 'slug')
        model = Tag


class RecipeCommonSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time')
        model = Recipe


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(required=False)
    ingredients = IngredientSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField('favorited_recipe')
    is_in_shopping_cart = serializers.SerializerMethodField(
        'in_shopping_cart'
    )
    image = Base64ImageField()

    def favorited_recipe(self, recipe):
        request = self.context.get('request')
        return Recipe.objects.annotate_favorited_flag(
            request, recipe
        ).get(id=recipe.id).is_favorited

    def in_shopping_cart(self, recipe):
        request = self.context.get('request')
        return Recipe.objects.annotate_in_shopping_cart_flag(
            request, recipe
        ).get(id=recipe.id).is_in_shopping_cart

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

    def create(self, validated_data):
        request = self.context.get('request')
        ingredients_data = request.data['ingredients']
        tags_data = request.data['tags']
        recipe = Recipe.objects.create(**validated_data)
        self.add_recipe_ingredients(recipe, ingredients_data)
        self.add_recipe_tags(recipe, tags_data)
        return recipe

    def update(self, instance, validated_data):
        request = self.context.get('request')
        ingredients_data = request.data['ingredients']
        tags_data = request.data['tags']
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time',
                                                   instance.cooking_time)
        instance.image = validated_data.get('image', instance.image)
        instance.save()
        instance.recipe_ingredients.delete()
        instance.recipe_tags.delete()
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
            'is_in_shopping_cart'
        )
        model = Recipe
        depth = 1


class FavoriteSerializer(serializers.ModelSerializer):
    user = HiddenField(default=CurrentUserDefault())

    def validate(self, data):
        if Favorite.objects.filter(
            user=data.get('user'),
            recipe=data.get('recipe')
        ).exists():
            raise ValidationError(
                'Рецепт уже добавлен в избранное!'
            )

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')


class ShoppingCartSerializer(serializers.ModelSerializer):
    user = HiddenField(default=CurrentUserDefault())

    def validate(self, data):
        if ShoppingCart.objects.filter(
            user=data.get('user'),
            recipe=data.get('recipe')
        ).exists():
            raise ValidationError(
                'Рецепт уже добавлен в список покупок!'
            )

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')
