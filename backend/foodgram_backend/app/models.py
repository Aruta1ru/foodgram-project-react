from django.db import models

from users.models import CustomUser


class Ingredient(models.Model):
    name = models.CharField(max_length=200)
    measurement_unit = models.CharField(max_length=20)

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Tag(models.Model):
    name = models.CharField(max_length=200, unique=True)
    color = models.CharField(max_length=7, default='#FFFFFF', unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.PROTECT,
        related_name='recipes'
    )
    name = models.CharField(max_length=200)
    text = models.TextField()
    cooking_time = models.PositiveIntegerField()
    image = models.ImageField(upload_to='recipe_pic/')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        through_fields=('recipe', 'ingredient'),
        related_name='ingredients'
    )
    tags = models.ManyToManyField(
        Tag,
        through='RecipeTag',
        through_fields=('recipe', 'tag'),
        related_name='tags'
    )

    def is_favorited(self, request):
        return Favorite.objects.filter(
            user=request.user,
            recipe=self
        ).exists()

    def is_in_shopping_cart(self, request):
        return ShoppingCart.objects.filter(
            user=request.user,
            recipe=self
        ).exists()

    def favorite_count(self):
        return Favorite.objects.filter(recipe=self).count()

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()


class RecipeTag(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)


class Favorite(models.Model):
    user = models.ForeignKey(CustomUser,
                             on_delete=models.CASCADE,
                             related_name="favorite")
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name="favorite")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_favorite"
            )
        ]

    def __str__(self):
        return f"{self.user.username} -> {self.recipe.name}"


class ShoppingCart(models.Model):
    user = models.ForeignKey(CustomUser,
                             on_delete=models.CASCADE,
                             related_name="shopping_cart")
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name="shopping_cart")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_cart"
            )
        ]

    def __str__(self):
        return f"{self.user.username} -> {self.recipe.name}"