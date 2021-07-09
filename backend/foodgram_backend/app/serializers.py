import base64

from rest_framework import serializers

from .models import Ingredient, Recipe, RecipeIngredient, Tag, RecipeTag


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = Ingredient


class RecipeIngredientSerializer(serializers.ModelSerializer):
    amount = serializers.IntegerField()

    class Meta:
        fields = ('name', 'measurement_unit', 'amount')
        model = Ingredient


class RecipeCommonSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time')
        model = Recipe


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('author',)
        model = Tag


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(many=True)
    tags = TagSerializer(many=True)
    is_favorited = serializers.SerializerMethodField('favorited_recipe')
    is_in_shopping_cart = serializers.SerializerMethodField('in_shopping_cart')

    def favorited_recipe(self, recipe):
        return recipe.is_favorite()

    def in_shopping_cart(self, recipe):
        return recipe.is_in_shopping_cart()

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient_data in ingredients_data:
            RecipeIngredient.objects.create(recipe=recipe, **ingredient_data)
        for tag_data in tags_data:
            RecipeTag.objects.create(recipe=recipe, **tag_data)
        return 
        
    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        instance = validated_data
        RecipeIngredient.objects.filter(recipe=instance).delete()
        RecipeTag.objects.filter(recipe=instance).delete()
        for ingredient_data in ingredients_data:
            RecipeIngredient.objects.create(recipe=instance, **ingredient_data)
        for tag_data in tags_data:
            RecipeTag.objects.create(recipe=instance, **tag_data)
        return instance

    def to_internal_value(self, data):
        id = data.get('id')
        name = data.get('name')
        text = data.get('text')
        cooking_time = data.get('cooking_time')
        author = data.get('author')
        ingredients = data.get('ingredients')
        tags = data.get('tags')
        is_favorite = data.get('is_favorite')
        is_in_shopping_cart = data.get('is_in_shopping_cart')
        image = data.get('image')

        with open(image, 'rb') as img_file:
            b64_string = base64.b64encode(img_file.read())
        
        return {
            'id': id,
            'name': name,
            'text': text,
            'cooking_time': cooking_time,
            'author': author,
            'ingredients': ingredients,
            'tags': tags,
            'is_favorite': is_favorite,
            'is_in_shopping_cart': is_in_shopping_cart,
            'image': b64_string,            
        }


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