from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('ingredients',
                views.IngredientViewSet,
                basename='ingredients')
router.register('tags', views.TagViewSet, basename='tags')
router.register('recipes', views.RecipeViewSet, basename='recipes')

urlpatterns = [
    path('recipes/<int:id>/favorite/', views.recipe_favorite),
    path('recipes/<int:id>/shopping_cart/', views.shopping_cart),
    path('', include(router.urls)),
]
