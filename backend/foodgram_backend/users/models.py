from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


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

    def create_superuser(self, username, email, password, first_name, last_name):
        user = self.model(
        	username=username, 
			email=self.normalize_email(email),
			first_name=first_name,
			last_name=last_name,
		)
        user.set_password(password)
        user.is_superuser = True
        user.is_verified = True
        user.is_staff = True
        user.role = user.ADMIN
        user.save()
        return user


class CustomUser(AbstractUser):
    ADMIN = 'admin'
    USER = 'user'
    ROLES = [
        (ADMIN, 'Administrator'),
        (USER, 'User'),
    ]
    email = models.EmailField(max_length=254, unique=True)
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    role = models.CharField(
        max_length=9,
        choices=ROLES,
        default=USER,
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'password', 'first_name', 'last_name')
    objects = CustomAccountManager()

    class Meta:
        ordering = ['email']

    def __str__(self):
        return self.email

    @property
    def is_admin_role(self):
        return self.role == self.ADMIN

    @property
    def is_user_role(self):
        return self.role == self.USER

    def is_subscribed(self, user):
        return True if Follow.objects.filter(
            user=user,
            author=self
        ).count() > 0 else False


class Follow(models.Model):
    user = models.ForeignKey(CustomUser,
                             on_delete=models.CASCADE,
                             related_name="follower")
    author = models.ForeignKey(CustomUser,
                               on_delete=models.CASCADE,
                               related_name="following")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"], name="unique_follow"
            )
        ]

    def __str__(self):
        return f"{self.user.username} -> {self.author.username}"