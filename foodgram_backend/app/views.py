from wsgiref.util import FileWrapper

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
        products = []
        cart_recipes = request.user.shopping_cart.recipes.values_list('recipe')
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
        report = pdf_create(products)
        #short_report = open("media/shopping_cart.pdf", 'rb')
        return HttpResponse(FileWrapper(report.output('shopping_cart.pdf')),
                            content_type='application/pdf')

    @action(
        ['get', 'delete'],
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        if request.method == 'GET':
            favorite_serializer = FavoriteSerializer(user=request.user,
                                                     recipe=recipe)
            if favorite_serializer.is_valid():
                favorite_serializer.save()
                recipe_serializer = RecipeSerializer(
                    recipe,
                    context={'request': request}
                )
                return Response(recipe_serializer.data,
                                status=status.HTTP_201_CREATED)
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
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        if request.method == 'GET':
            cart_serializer = ShoppingCartSerializer(user=request.user,
                                                     recipe=recipe)
            if cart_serializer.is_valid():
                cart_serializer.save()
                recipe_serializer = RecipeSerializer(
                    recipe,
                    context={'request': request}
                )
                return Response(recipe_serializer.data,
                                status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if ShoppingCart.objects.filter(
                user=request.user,
                recipe=recipe
            ).delete() != 0:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'errors': 'Рецепт уже удален из корзины!'},
                            status=status.HTTP_400_BAD_REQUEST)
