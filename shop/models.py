from django.db import models
from parler.models import TranslatableModel, TranslatedFields
from treebeard.mp_tree import MP_Node
from django.conf import settings


class Category(MP_Node):
    source_id = models.CharField(max_length=500,
                                 unique=True,
                                 verbose_name='Ідентифікатор у \
                                                вигрузці')
    name_ua = models.CharField(verbose_name='Назва українською',
                               max_length=200)
    name_ru = models.CharField(verbose_name='Назва російською', max_length=200)
    slug = models.SlugField(verbose_name='Слаг',
                            unique=True, max_length=250)
    quantity = models.PositiveIntegerField(default=0, verbose_name='Кількість')
    image = models.ImageField(upload_to='terms/%Y/%m/%d/', blank=True,
                              null=True, verbose_name='Лого')
    node_order_by = ['name_ua']
    updated = models.DateTimeField(auto_now=True)
    is_car_brand = models.BooleanField(verbose_name='Бренд машины?',
                                       default=False)

    class Meta:
        verbose_name = 'Категорія'
        verbose_name_plural = 'Категорії'

    def __str__(self):
        return self.name_ua

    def get_absolute_url(self):
        return f'{settings.CORS_ALLOWED_ORIGINS[3]}/uk/product-cat/{self.slug}'


class Product(TranslatableModel):
    sku = models.CharField(max_length=10, verbose_name='Артикул', unique=True)
    translation = TranslatedFields(
        name=models.CharField(max_length=200, verbose_name='Назва'),
        search_query=models.TextField(verbose_name='Пошукові фрази',
                                      blank=True),
        description=models.TextField(verbose_name='Опис', blank=True)
    )
    slug = models.SlugField(verbose_name='Слаг',
                            unique=True, max_length=250)
    price = models.PositiveIntegerField(verbose_name='Ціна', blank=True)
    price_old = models.PositiveIntegerField(verbose_name='Ціна стара', 
                                            blank=True, null=True)
    image = models.ImageField(upload_to='products/%Y/%m/%d/', blank=True,
                              verbose_name='Фото')
    image_source = models.URLField(
        verbose_name='Посилання на оригінальну картинку',
        blank=True,
        null=True
    )
    quantity = models.PositiveIntegerField(blank=True,
                                           verbose_name='Кількість')
    category = models.ForeignKey(Category, on_delete=models.PROTECT,
                                 related_name='products',
                                 verbose_name='Категорія')
    producer = models.CharField(max_length=50, verbose_name='Виробник',
                                blank=True)
    country = models.CharField(max_length=20, verbose_name='Країна виробник',
                               blank=True)
    vin = models.CharField(max_length=500, verbose_name='Vin', blank=True,
                           null=True)
    params = models.JSONField(verbose_name='Параметри', blank=True)
    created = models.DateTimeField(auto_now_add=True, verbose_name='Створено')
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товари'
        indexes = [
            models.Index(fields=['sku']),
            models.Index(fields=['price']),
            models.Index(fields=['quantity']),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'{settings.CORS_ALLOWED_ORIGINS[3]}/uk/product-cat/{self.category.slug}/{self.slug}'


