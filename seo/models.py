from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField


class SeoItem(models.Model):
    link = models.URLField(verbose_name='Посилання',
                           unique=True,
                           help_text='Посилання повинно бути без / в кінці, та без get-параметрів')
    title_tag = models.CharField(max_length=500,
                                 verbose_name='<title>',
                                 blank=True)
    meta_description = models.CharField(max_length=500,
                                        verbose_name='Meta-description',
                                        blank=True)
    content = RichTextUploadingField(verbose_name='Контент',
                                     blank=True)

    class Meta:
        verbose_name = 'Налаштування СЕО'
        verbose_name_plural = 'Налаштування СЕО'

    def __str__(self):
        return self.link

