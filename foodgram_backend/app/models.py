from django.db import models
from users.models import CustomUser


class Ingredient(models.Model):
    name = models.CharField('Название', max_length=200)
    measurement_unit = models.CharField('Единица измерения', max_length=20)

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']


class Tag(models.Model):
    name = models.CharField('Название', max_length=200, unique=True)
    color = models.CharField('Цвет (HEX)',
                             max_length=7,
                             default='#FFFFFF',
                             unique=True)
    slug = models.SlugField('Слаг', unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']


class Recipe(models.Model):
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.PROTECT,
        related_name='recipes',
        verbose_name='Автор'
    )
    name = models.CharField('Название', max_length=200)
    text = models.TextField('Описание')
    cooking_time = models.PositiveIntegerField('Время приготовления')
    image = models.ImageField('Картинка', upload_to='recipe_pic/')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        through_fields=('recipe', 'ingredient'),
        related_name='ingredients',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        through='RecipeTag',
        through_fields=('recipe', 'tag'),
        related_name='tags',
        verbose_name='Теги'
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    def is_favorited(self, request):
        return Favorite.objects.filter(
            user=request.user if request.user.is_authenticated else None,
            recipe=self
        ).exists()

    def is_in_shopping_cart(self, request):
        return ShoppingCart.objects.filter(
            user=request.user if request.user.is_authenticated else None,
            recipe=self
        ).exists()

    def favorite_count(self):
        return Favorite.objects.filter(recipe=self).count()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               verbose_name='Рецепт')
    ingredient = models.ForeignKey(Ingredient,
                                   on_delete=models.CASCADE,
                                   verbose_name='Ингредиент')
    amount = models.PositiveIntegerField('Количество')

    def __str__(self):
        return f'{self.recipe} -> {self.ingredient}' 

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'
        ordering = ['recipe', 'ingredient']


class RecipeTag(models.Model):
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               verbose_name='Рецепт')
    tag = models.ForeignKey(Tag,
                            on_delete=models.CASCADE,
                            verbose_name='Тег')

    def __str__(self):
        return f'{self.recipe} -> {self.tag}' 

    class Meta:
        verbose_name = 'Тег рецепта'
        verbose_name_plural = 'Теги рецепта'
        ordering = ['recipe', 'tag']


class Favorite(models.Model):
    user = models.ForeignKey(CustomUser,
                             on_delete=models.CASCADE,
                             related_name='favorited',
                             verbose_name='Пользователь')
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='favorited',
                               verbose_name='Рецепт')

    def __str__(self):
        return f'{self.user.username} -> {self.recipe.name}'

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_favorite'
            )
        ]
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        ordering = ['user', 'recipe']


class ShoppingCart(models.Model):
    user = models.ForeignKey(CustomUser,
                             on_delete=models.CASCADE,
                             related_name='shopping_cart',
                             verbose_name='Пользователь')
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='shopping_cart',
                               verbose_name='Рецепт')

    def __str__(self):
        return f'{self.user.username} -> {self.recipe.name}'

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_cart'
            )
        ]
        verbose_name = 'Список продуктов'
        verbose_name_plural = 'Списки продуктов'
        ordering = ['user', 'recipe']
