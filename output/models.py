from django.db import models


class Output(models.Model):
    file = models.FileField(upload_to='output/%Y/%m/%d/', 
                            verbose_name='Файл')
    created = models.DateTimeField(auto_now_add=True,
                                   verbose_name='Створено')
