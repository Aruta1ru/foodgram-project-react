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
from .serializers import IngredientSerializer, RecipeSerializer, TagSerializer, RecipeCommonSerializer


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
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['author', 'tags', 'is_favorited', 'is_in_shopping_cart']


@api_view(['GET', 'DELETE'])
@permission_classes([IsAuthenticated])    
def recipe_favorite(request, id):
    if request.method == 'GET':
        recipe = get_object_or_404(Recipe, id=id)
        if Favorite.objects.filter(user=request.user,
                                   recipe=recipe
        ).count() == 0:
            Favorite.objects.create(user=request.user,
                                    recipe=recipe)
            recipe = get_object_or_404(Recipe, id=id)
            serializer = RecipeCommonSerializer(data=recipe)
            if serializer.is_valid():
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        return Response({'errors': 'Вы уже добавили рецепт в избранное!'},
                        status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'DELETE':
        recipe=get_object_or_404(Recipe, id=id)
        if Favorite.objects.filter(user=request.user,
                                   recipe=recipe
        ).count() > 0:        
            Favorite.objects.filter(
                user=request.user,
                recipe=recipe
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': 'Вы уже убрали рецепт из избранного!'},
                        status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'DELETE'])
@permission_classes([IsAuthenticated])    
def shopping_cart(request, id):
    if request.method == 'GET':
        recipe = get_object_or_404(Recipe, id=id)
        if ShoppingCart.objects.filter(user=request.user,
                                   recipe=recipe
        ).count() == 0:
            ShoppingCart.objects.create(user=request.user,
                                    recipe=recipe)
            recipe = get_object_or_404(Recipe, id=id)
            serializer = RecipeCommonSerializer(data=recipe)
            if serializer.is_valid():
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        return Response({'errors': 'Вы уже добавили рецепт в корзину!'},
                        status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'DELETE':
        recipe=get_object_or_404(Recipe, id=id)
        if ShoppingCart.objects.filter(user=request.user,
                                   recipe=recipe
        ).count() > 0:        
            ShoppingCart.objects.filter(
                user=request.user,
                recipe=recipe
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': 'Вы уже убрали рецепт из корзины!'},
                        status=status.HTTP_400_BAD_REQUEST)