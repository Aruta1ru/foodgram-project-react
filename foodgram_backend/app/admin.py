from django.contrib import admin
from django.db.models import Count

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient, RecipeTag,
                     ShoppingCart, Tag)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'color', 'slug')
    search_fields = ('name',)


class IngredientInlineAdmin(admin.TabularInline):
    model = Recipe.ingredients.through


class TagInlineAdmin(admin.TabularInline):
    model = Recipe.tags.through


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'favorited_count')
    search_fields = ('name', 'author', 'tags')
    inlines = [IngredientInlineAdmin, TagInlineAdmin]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(favorited_count=Count('favorited'))

    @staticmethod
    def favorited_count(obj):
        return Recipe.objects.annotate_favorited_count(obj).get(
            id=obj.id
        ).favorited_count


class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount')


class RecipeTagAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'tag')


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
admin.site.register(RecipeTag, RecipeTagAdmin)
