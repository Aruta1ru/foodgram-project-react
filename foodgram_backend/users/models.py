from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.db.models import Count
from django.db.models.expressions import Exists


class CustomAccountManager(BaseUserManager):

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
        user = self.model(
            username=username,
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            is_superuser=True,
            is_verified=True,
            is_staff=True,
            role=self.ADMIN
        )
        user.set_password(password)
        user.save()
        return user

    def annotate_subscribed_flag(self, user):
        return self.annotate(
            is_subscribed=Exists(Follow.objects.filter(user=user))
        )

    def annotate_recipes_count(self):
        return self.annotate(
            recipes_count=Count('recipes')
        )


class CustomUser(AbstractUser):
    ADMIN = 'admin'
    USER = 'user'
    ROLES = [
        (ADMIN, 'Administrator'),
        (USER, 'User'),
    ]
    email = models.EmailField('Адрес электронной почты',
                              max_length=254,
                              unique=True)
    username = models.CharField('Логин',
                                max_length=150,
                                unique=True)
    first_name = models.CharField('Имя', max_length=150)
    last_name = models.CharField('Фамилия', max_length=150)
    role = models.CharField(
        'Роль',
        max_length=9,
        choices=ROLES,
        default=USER,
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'password', 'first_name', 'last_name')
    objects = CustomAccountManager()

    class Meta:
        ordering = ['email']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email

    @property
    def is_admin_role(self):
        return self.role == self.ADMIN

    @property
    def is_user_role(self):
        return self.role == self.USER


class Follow(models.Model):
    user = models.ForeignKey(CustomUser,
                             on_delete=models.CASCADE,
                             related_name='follower',
                             verbose_name='Пользователь')
    author = models.ForeignKey(CustomUser,
                               on_delete=models.CASCADE,
                               related_name='following',
                               verbose_name='Автор')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name='unique_follow'
            )
        ]
        ordering = ['user', 'author']
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user.username} -> {self.author.username}'
