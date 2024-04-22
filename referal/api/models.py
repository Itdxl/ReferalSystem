from django.contrib.auth.models import AbstractBaseUser
from django.db import models
import random
import string


class CustomUser(AbstractBaseUser):
    phone_number = models.CharField(max_length=20, unique=True)
    authorization_code = models.CharField(max_length=4, blank=True, null=True)
    invite_code = models.CharField(max_length=6, unique=True, blank=True, null=True)
    is_authenticated = models.BooleanField(default=False) # для проверки кода
    inviter = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='invitees')


    def __str__(self):
        return self.phone_number

    def save(self, *args, **kwargs):
        # Генерация и сохранение уникального инвайт-кода при первой авторизации
        if not self.pk and not self.invite_code:
            self.invite_code = self.generate_code()
        super().save(*args, **kwargs)

    def generate_code(self):
        unique_code = None
        while not unique_code:
            probable_code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
            if not CustomUser.objects.filter(invite_code=probable_code).exists():
                unique_code = probable_code
        return unique_code
