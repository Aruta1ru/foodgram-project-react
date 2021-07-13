import base64
import uuid

from django.core.files.base import ContentFile
from rest_framework import serializers

from app.models import Ingredient, Recipe, RecipeIngredient, Tag, RecipeTag
from users.serializers import UserSerializer 


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            id = uuid.uuid4()
            data = ContentFile(base64.b64decode(imgstr), name = id.urn[9:] + '.' + ext)
        return super(Base64ImageField, self).to_internal_value(data)


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = Ingredient


class RecipeIngredientSerializer(serializers.Serializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(read_only=True, source='ingredient.name')
    measurement_unit = serializers.CharField(read_only=True, source='ingredient.measurement_unit')
    amount = serializers.IntegerField(read_only=True)


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'color', 'slug')
        model = Tag


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(required=False)
    ingredients = serializers.SerializerMethodField('get_ingredients')
    tags = TagSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField('favorited_recipe')
    is_in_shopping_cart = serializers.SerializerMethodField('in_shopping_cart')
    image = Base64ImageField()

    def get_ingredients(self, obj):
        query = RecipeIngredient.objects.filter(recipe=obj)
        return RecipeIngredientSerializer(instance=query, many=True).data

    def favorited_recipe(self, recipe):
        request = self.context.get("request")
        return recipe.is_favorited(request)

    def in_shopping_cart(self, recipe):
        request = self.context.get("request")
        return recipe.is_in_shopping_cart(request)

    def create(self, validated_data):
        request = self.context.get("request")
        ingredients_data = request.data['ingredients']
        tags_data = request.data['tags']
        recipe = Recipe.objects.create(**validated_data)
        for ingredient_data in ingredients_data:
            ingredient = Ingredient.objects.get(id=ingredient_data['id'])
            amount = ingredient_data['amount']
            RecipeIngredient.objects.create(recipe=recipe, ingredient=ingredient, amount=amount)
        for tag_id in tags_data:
            tag = Tag.objects.get(id=tag_id)
            RecipeTag.objects.create(recipe=recipe, tag=tag)
        return recipe
        
    def update(self, instance, validated_data):
        request = self.context.get("request")
        ingredients_data = request.data['ingredients']
        tags_data = request.data['tags']
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time', instance.cooking_time)
        instance.image = validated_data.get('image', instance.image)
        instance.save()
        RecipeIngredient.objects.filter(recipe=instance).delete()
        RecipeTag.objects.filter(recipe=instance).delete()
        for ingredient_data in ingredients_data:
            ingredient = Ingredient.objects.get(id=ingredient_data['id'])
            amount = ingredient_data['amount']
            RecipeIngredient.objects.create(recipe=instance, ingredient=ingredient, amount=amount)
        for tag_id in tags_data:
            tag = Tag.objects.get(id=tag_id)
            RecipeTag.objects.create(recipe=instance, tag=tag)
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