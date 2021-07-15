from django_filters import filters as base_filters
from django_filters import rest_framework as filters

from .models import Favorite, Ingredient, Recipe, ShoppingCart, Tag


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ['name']


class RecipeFilter(filters.FilterSet):
    tags = base_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    is_favorited = base_filters.NumberFilter(method='filter_favorited')
    is_in_shopping_cart = base_filters.NumberFilter(
        method='filter_shopping_cart'
    )

    def filter_favorited(self, queryset, name, value):
        recipe_ids = Favorite.objects.filter(
            user=self.request.user
        ).values('recipe')
        if value == 1:
            recipes = Recipe.objects.filter(id__in=recipe_ids)
        else:
            recipes = Recipe.objects.exclude(id__in=recipe_ids)
        return recipes

    def filter_shopping_cart(self, queryset, name, value):
        recipe_ids = ShoppingCart.objects.filter(
            user=self.request.user
        ).values('recipe')
        if value == 1:
            recipes = Recipe.objects.filter(id__in=recipe_ids)
        else:
            recipes = Recipe.objects.exclude(id__in=recipe_ids)
        return recipes

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'is_favorited', 'is_in_shopping_cart']
