from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                verbose_name='Користувач')
    first_name = models.CharField(max_length=100, verbose_name='Ім\'я',
                                  blank=True)
    last_name = models.CharField(max_length=100, verbose_name='Прізвище',
                                 blank=True)
    phone = models.CharField(max_length=25, verbose_name='Телефон',
                             blank=True)
    delivery = models.CharField(max_length=2, verbose_name='Доставка',
                                blank=True)

    created = models.DateTimeField(auto_now_add=True, verbose_name='Створено')

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f'Користувач {self.id}'
