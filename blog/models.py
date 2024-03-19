from parler.models import TranslatableModel, TranslatedFields
from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField


class Post(TranslatableModel):
    class Status(models.TextChoices):
        DRAFT = 'df', 'Чернетка'
        PUBLISHED = 'pb', 'Опубліковано'

    translation = TranslatedFields(
        title=models.CharField(max_length=250, verbose_name='Заголовок'),
        excerpt=models.TextField(max_length=250, verbose_name='Короткий опис'),
        body=RichTextUploadingField(verbose_name='Контент')
    )
    thumbnail = models.ImageField(upload_to='blog/%Y/%m/%d/',
                                  verbose_name='Мініатюра')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Створено')
    updated = models.DateTimeField(auto_now=True, verbose_name='Оновлено')

    status = models.CharField(max_length=2, choices=Status.choices,
                              verbose_name='Статус',
                              default=Status.DRAFT)

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Пости'
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created'])
        ]

    def __str__(self):
        return self.title
