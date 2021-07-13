from django_filters import rest_framework as filters
from django_filters import filters as base_filters

from .models import Ingredient, Recipe, Tag, Favorite


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
    #is_favorited = base_filters.NumberFilter(method='filter_favorited')
    #is_in_shopping_cart = base_filters.NumberFilter(method='filter_shopping_cart')

    class Meta:
        model = Recipe
        fields = ['author', 'tags']