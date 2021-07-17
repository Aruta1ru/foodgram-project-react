from wsgiref.util import FileWrapper

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from . import filters
from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)
from .permissions import IsAuthorOrReadOnly
from .serializers import IngredientSerializer, RecipeSerializer, TagSerializer
from .utils import pdf_create


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
    permission_classes = [AllowAny, IsAuthorOrReadOnly]
    filterset_class = filters.RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(['get'], detail=False, permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        products = []
        cart_recipes = ShoppingCart.objects.filter(
            user=request.user
        ).values_list('recipe')
        recipes = RecipeIngredient.objects.filter(
            recipe_id__in=(cart_recipes)
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(amount_sum=Sum('amount'))
        for recipe in recipes:
            product = {}
            product['name'] = recipe['ingredient__name']
            product['measurement_unit'] = (
                recipe['ingredient__measurement_unit']
            )
            product['amount'] = recipe['amount_sum']
            products.append(product)
        pdf_create(products)
        short_report = open("media/shopping_cart.pdf", 'rb')
        response = HttpResponse(FileWrapper(short_report),
                                content_type='application/pdf')
        return response


@api_view(['GET', 'DELETE'])
@permission_classes([IsAuthenticated])
def recipe_favorite(request, id):
    if request.method == 'GET':
        recipe = get_object_or_404(Recipe, id=id)
        if not Favorite.objects.filter(
            user=request.user,
            recipe=recipe
        ).exists():
            Favorite.objects.create(user=request.user,
                                    recipe=recipe)
            recipe = get_object_or_404(Recipe, id=id)
            serializer = RecipeSerializer(recipe,
                                          context={'request': request})
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        return Response({'errors': 'Рецепт уже добавлен в избранное!'},
                        status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'DELETE':
        recipe = get_object_or_404(Recipe, id=id)
        if Favorite.objects.filter(
            user=request.user,
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
        if not ShoppingCart.objects.filter(
            user=request.user,
            recipe=recipe
        ).exists():
            ShoppingCart.objects.create(user=request.user,
                                        recipe=recipe)
            recipe = get_object_or_404(Recipe, id=id)
            serializer = RecipeSerializer(recipe,
                                          context={'request': request})
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        return Response({'errors': 'Рецепт уже добавлен в корзину!'},
                        status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'DELETE':
        recipe = get_object_or_404(Recipe, id=id)
        if ShoppingCart.objects.filter(
            user=request.user,
            recipe=recipe
        ).exists():
            ShoppingCart.objects.filter(
                user=request.user,
                recipe=recipe
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': 'Рецепт уже удален из корзины!'},
                        status=status.HTTP_400_BAD_REQUEST)
