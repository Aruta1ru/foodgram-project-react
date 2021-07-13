from rest_framework import status, viewsets
from rest_framework.decorators import api_view, action, permission_classes
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from . import filters
from .models import Ingredient, Recipe, Tag, Favorite, ShoppingCart
from .permissions import IsAuthorOrReadOnly
from .serializers import IngredientSerializer, RecipeSerializer, TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filterset_class = filters.IngredientFilter
    pagination_class = None


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = PageNumberPagination
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]
    filterset_class = filters.RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


@api_view(['GET', 'DELETE'])
@permission_classes([IsAuthenticated])    
def recipe_favorite(request, id):
    if request.method == 'GET':
        recipe = get_object_or_404(Recipe, id=id)
        if not Favorite.objects.filter(user=request.user,
                                   recipe=recipe
        ).exists():
            Favorite.objects.create(user=request.user,
                                    recipe=recipe)
            recipe = get_object_or_404(Recipe, id=id)
            serializer = RecipeSerializer(recipe, context={'request': request})
            return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
        return Response({'errors': 'Рецепт уже добавлен в избранное!'},
                        status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'DELETE':
        recipe=get_object_or_404(Recipe, id=id)
        if Favorite.objects.filter(user=request.user,
                                 recipe=recipe
        ).exists():        
            Favorite.objects.filter(
                user=request.user,
                recipe=recipe
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': 'Рецепт уже удален из избранного!'},
                        status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'DELETE'])
@permission_classes([IsAuthenticated])    
def shopping_cart(request, id):
    if request.method == 'GET':
        recipe = get_object_or_404(Recipe, id=id)
        if not ShoppingCart.objects.filter(user=request.user,
                                       recipe=recipe
        ).exists():
            ShoppingCart.objects.create(user=request.user,
                                        recipe=recipe)
            recipe = get_object_or_404(Recipe, id=id)
            serializer = RecipeSerializer(recipe, context={'request': request})
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        return Response({'errors': 'Рецепт уже добавлен в корзину!'},
                        status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'DELETE':
        recipe=get_object_or_404(Recipe, id=id)
        if ShoppingCart.objects.filter(user=request.user,
                                       recipe=recipe
        ).exists():        
            ShoppingCart.objects.filter(
                user=request.user,
                recipe=recipe
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': 'Рецепт уже удален из корзины!'},
                        status=status.HTTP_400_BAD_REQUEST)