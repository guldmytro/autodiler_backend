from django.db import models
from parler.models import TranslatableModel, TranslatedFields


class Faq(TranslatableModel):
    translation = TranslatedFields(
        question=models.CharField(max_length=255, verbose_name='Питання'),
        answer=models.TextField(max_length=1000, verbose_name='Відповідь')
    )

    class Meta:
        verbose_name = 'Питання-відповідь'
        verbose_name_plural = 'Питання-відповіді'

    def __str__(self):
        return self.question
