from django.db.models import Count, Manager, OuterRef
from django.db.models.expressions import Exists
from django.db.models.query import QuerySet


class RecipeQueryset(QuerySet):
    def annotate_favorited_flag(self, user):
        from app.models import Favorite
        return self.annotate(
            is_favorited=Exists(Favorite.objects.filter(
                recipe=OuterRef('id'),
                user=user if user.is_authenticated else None
            ))
        )

    def annotate_in_shopping_cart_flag(self, user):
        from app.models import ShoppingCart
        return self.annotate(
            is_in_shopping_cart=Exists(ShoppingCart.objects.filter(
                recipe=OuterRef('id'),
                user=user if user.is_authenticated else None
            ))
        )

    def annotate_favorited_count(self):
        return self.annotate(
            favorited_count=Count('favorited')
        )


class RecipeManager(Manager.from_queryset(RecipeQueryset)):
    pass
