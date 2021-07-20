from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from . import filters
from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)
from .permissions import IsAuthorOrReadOnly
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeSerializer, ShoppingCartSerializer,
                          TagSerializer)
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
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_cart.pdf"'
        )
        products = []
        cart_recipes = request.user.shopping_cart.values_list('recipe')
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
        pdf = pdf_create(products)
        response.write(pdf)
        return response

    @action(
        ['get', 'delete'],
        detail=True,
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'GET':
            serializer = FavoriteSerializer(
                data={'recipe': recipe.id, 'user': request.user.id}
            )
            if serializer.is_valid():
                serializer.save()
                recipe_serializer = RecipeSerializer(
                    recipe,
                    context={'request': request}
                )
                return Response(recipe_serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'DELETE':
            if Favorite.objects.filter(
                user=request.user,
                recipe=recipe
            ).delete() != 0:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'errors': 'Рецепт уже удален из избранного!'},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(
        ['get', 'delete'],
        detail=True,
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'GET':
            serializer = ShoppingCartSerializer(
                data={'recipe': recipe.id, 'user': request.user.id}
            )
            if serializer.is_valid():
                serializer.save()
                recipe_serializer = RecipeSerializer(
                    recipe,
                    context={'request': request}
                )
                return Response(recipe_serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'DELETE':
            if ShoppingCart.objects.filter(
                user=request.user,
                recipe=recipe
            ).delete() != 0:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'errors': 'Рецепт уже удален из корзины!'},
                            status=status.HTTP_400_BAD_REQUEST)
