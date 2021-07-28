from django.contrib.auth.models import BaseUserManager
from django.db.models import Count, OuterRef
from django.db.models.expressions import Exists
from django.db.models.query import QuerySet


class UserQueryset(QuerySet):
    def annotate_subscribed_flag(self, user):
        from users.models import Follow
        return self.annotate(
            is_subscribed=Exists(Follow.objects.filter(
                author=OuterRef('pk'),
                user=user if user.is_authenticated else None)
            )
        )

    def annotate_recipes_count(self):
        return self.annotate(
            recipes_count=Count('recipes')
        )


class CustomAccountManager(BaseUserManager.from_queryset(UserQueryset)):

    def create_user(self, username, email, password, first_name, last_name):
        user = self.model(
            username=username,
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
        )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, email,
                         password, first_name, last_name):
        from users.models import CustomUser
        user = self.model(
            username=username,
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            is_superuser=True,
            is_staff=True,
            role=CustomUser.ADMIN
        )
        user.set_password(password)
        user.save()
        return user
