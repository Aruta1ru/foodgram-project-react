from django.contrib import admin

from .models import Ingredient, Tag


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ('name', 'color', 'slug')
    search_fields = ('name',)


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
