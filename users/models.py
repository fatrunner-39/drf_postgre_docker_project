from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import FileExtensionValidator
from django.db import models


class User(AbstractUser):
    username_validator = UnicodeUsernameValidator()

    username = models.EmailField(
        unique=True
    )
    role_id = models.ForeignKey('Role', on_delete=models.CASCADE, null=True)
    bio = models.TextField(blank=True)
    img = models.ImageField(upload_to='users/', blank=True, validators=[FileExtensionValidator(['png', 'jpg', 'gif', 'jpeg'])])

    USERNAME_FIELD = 'username'

    def __str__(self):
        return self.username


class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class CoachToRunner(models.Model):
    coach_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='coach')
    runner_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='runner')


class Subscribe(models.Model):
    subscriber_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriber')
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscribe')
