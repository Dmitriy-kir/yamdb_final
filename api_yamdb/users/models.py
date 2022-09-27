import uuid

from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class UsernameValidator(RegexValidator):
    regex = r'^[\w.@+-]'


class CustomUser(AbstractUser):
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'
    SUPERUSER = 'superuser'

    ROLES = [
        (ADMIN, 'Администратор'),
        (MODERATOR, 'Модератор'),
        (USER, 'Пользователь'),
        (SUPERUSER, 'Суперпользователь')
    ]

    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[UsernameValidator],
    )
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(max_length=254, unique=True)
    bio = models.TextField(blank=True)
    role = models.CharField(
        max_length=30,
        choices=ROLES,
        default=USER,
        blank=True
    )
    confirmation_code = models.CharField(
        max_length=256,
        default=uuid.uuid4,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == ('admin' or 'superuser')

    @property
    def is_moderator(self):
        return self.role == 'moderator'

    @property
    def is_user(self):
        return self.role == 'user'
