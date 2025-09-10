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
    visible = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Категорія'
        verbose_name_plural = 'Категорії'

    def __str__(self):
        return self.name_ua

    def get_absolute_url(self):
        return f'{settings.CORS_ALLOWED_ORIGINS[3]}/uk/product-cat/{self.slug}'


class Product(TranslatableModel):
    parent = models.ForeignKey('self', on_delete=models.CASCADE,
                               blank=True, null=True, related_name='children')
    color = models.ForeignKey('Color', on_delete=models.CASCADE,
                              blank=True, null=True, related_name='products')
    id_1c = models.CharField(max_length=200, blank=True, null=True)
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
    price_partner = models.PositiveIntegerField(verbose_name='Ціна оптова', 
                                                blank=True, null=True)
    image = models.ImageField(upload_to='products/%Y/%m/%d/', blank=True,
                              verbose_name='Фото', null=True)
    image2 = models.ImageField(upload_to='products/%Y/%m/%d/', blank=True,
                               verbose_name='Фото', null=True)
    image3 = models.ImageField(upload_to='products/%Y/%m/%d/', blank=True,
                               verbose_name='Фото', null=True)
    image4 = models.ImageField(upload_to='products/%Y/%m/%d/', blank=True,
                               verbose_name='Фото', null=True)
    image5 = models.ImageField(upload_to='products/%Y/%m/%d/', blank=True,
                               verbose_name='Фото', null=True)
    watermarked = models.BooleanField(default=False)

    image_source = models.URLField(
        verbose_name='Посилання на оригінальну картинку',
        blank=True,
        null=True
    )
    quantity = models.PositiveIntegerField(blank=True,
                                           null=True,
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
    params = models.JSONField(verbose_name='Параметри', blank=True, null=True)
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
        quantity = self.quantity
        if self.parent:
            quantity = self.parent.quantity
        return f'{self.sku} ({self.price} грн., залишок - {quantity} шт.) - {self.name}'

    def get_absolute_url(self):
        return f'{settings.CORS_ALLOWED_ORIGINS[3]}/uk/product-cat/{self.category.slug}/{self.slug}'
            
    def save(self, *args, **kwargs):
        if self.parent:
            self.id_1c = self.parent.id_1c
            self.category = self.parent.category
            self.quantity = 0
        super().save(*args, **kwargs)


class Color(TranslatableModel):
    translation = TranslatedFields(
        name=models.CharField(max_length=40, verbose_name='Назва кольору')
    )
    hex_code = models.CharField(max_length=7, help_text="Наприклад: #FF0000")

    class Meta:
        verbose_name = "Колір"
        verbose_name_plural = "Кольори"

    def __str__(self):
        return f"{self.name} ({self.hex_code})"
