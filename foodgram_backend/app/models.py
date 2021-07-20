from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.expressions import Value

user = get_user_model()


class RecipeManager(models.Manager):
    def annotate_favorited_flag(self, request, recipe):
        return self.annotate(
            is_favorited=Value(Favorite.objects.filter(
                user=request.user if request.user.is_authenticated else None,
                recipe=recipe
            ).exists())
        )

    def annotate_in_shopping_cart_flag(self, request, recipe):
        return self.annotate(
            is_in_shopping_cart=Value(ShoppingCart.objects.filter(
                user=request.user if request.user.is_authenticated else None,
                recipe=recipe
            ).exists())
        )

    def annotate_favorited_count(self, recipe):
        return self.annotate(
            favorited_count=Value(recipe.favorited.count())
        )


class Ingredient(models.Model):
    name = models.CharField('Название', max_length=200)
    measurement_unit = models.CharField('Единица измерения', max_length=20)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Tag(models.Model):
    name = models.CharField('Название', max_length=200, unique=True)
    color = models.CharField('Цвет (HEX)',
                             max_length=7,
                             default='#FFFFFF',
                             unique=True)
    slug = models.SlugField('Слаг', unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        user,
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
    objects = RecipeManager()

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='recipe_ingredients',
                               verbose_name='Рецепт',)
    ingredient = models.ForeignKey(Ingredient,
                                   on_delete=models.CASCADE,
                                   related_name='recipe_ingredients',
                                   verbose_name='Ингредиент')
    amount = models.PositiveIntegerField('Количество')

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'
        ordering = ['recipe', 'ingredient']

    def __str__(self):
        return f'{self.recipe} -> {self.ingredient}'


class RecipeTag(models.Model):
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='recipe_tags',
                               verbose_name='Рецепт')
    tag = models.ForeignKey(Tag,
                            on_delete=models.CASCADE,
                            related_name='recipe_tags',
                            verbose_name='Тег')

    class Meta:
        verbose_name = 'Тег рецепта'
        verbose_name_plural = 'Теги рецепта'
        ordering = ['recipe', 'tag']

    def __str__(self):
        return f'{self.recipe} -> {self.tag}'


class Favorite(models.Model):
    user = models.ForeignKey(user,
                             on_delete=models.CASCADE,
                             related_name='favorited',
                             verbose_name='Пользователь')
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='favorited',
                               verbose_name='Рецепт')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_favorite'
            )
        ]
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        ordering = ['user', 'recipe']

    def __str__(self):
        return f'{self.user.username} -> {self.recipe.name}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(user,
                             on_delete=models.CASCADE,
                             related_name='shopping_cart',
                             verbose_name='Пользователь')
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='shopping_cart',
                               verbose_name='Рецепт')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_cart'
            )
        ]
        verbose_name = 'Список продуктов'
        verbose_name_plural = 'Списки продуктов'
        ordering = ['user', 'recipe']

    def __str__(self):
        return f'{self.user.username} -> {self.recipe.name}'
