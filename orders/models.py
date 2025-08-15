from django.db import models
from shop.models import Product
from django.contrib.auth.models import User
from django.urls import reverse
import re

class Order(models.Model):

    class Status(models.TextChoices):
        NEW = 'nw', 'Нова заявка'
        WORK = 'wk', 'У роботі'
        IS_EQUIPPED = 'ep', 'Комплектується'
        ON_DELIVERY = 'dy', 'Доставляється'
        WAITING_ON_NOVA = 'wn', 'Чекає на складі нової пошти'
        WAITING_ON_PICKUP = 'wp', 'Чекає в точці самовивозу'
        DONE = 'dn', 'Виконано'
        CANCELED = 'cl', 'Скасовано'

    class Delivery(models.TextChoices):
        NOVA_DELIVERY = 'nd', 'Самовивіз із Нової пошти'
        NOVA_DELIVERY2 = 'xd', 'Кур\'єром Нової Пошти'
        PICKUP = 'pu', 'Самовивіз'

    class Payment(models.TextChoices):
        ON_DELIVERY = 'od', 'При отриманні'
        ONLILE = 'ol', 'LiqPay'
        MONOBANK = 'mb', 'Monobank'


    status = models.CharField(max_length=2,
                              choices=Status.choices,
                              default=Status.NEW,
                              verbose_name='Статус')
    user = models.ForeignKey(User, on_delete=models.PROTECT,
                             verbose_name='Користувач',
                             blank=True, null=True)
    first_name = models.CharField(max_length=50, verbose_name='Ім\'я')
    last_name = models.CharField(max_length=50, verbose_name='Прізвище')
    phone = models.CharField(max_length=100, verbose_name='Телефон')
    email = models.EmailField(verbose_name='E-mail')

    delivery = models.CharField(max_length=2,
                                choices=Delivery.choices,
                                default=Delivery.PICKUP,
                                verbose_name='Спосіб доставки')
    ttn = models.CharField(max_length=80, verbose_name='ТТН', blank=True, default='')
    city = models.CharField(max_length=255, blank=True,
                            verbose_name='Населений пункт')
    nova_office = models.CharField(max_length=255, blank=True,
                                   verbose_name='Відділення Нової пошти')
    address = models.CharField(max_length=500, blank=True, null=True,
                               verbose_name='Адреса кур\'єрської доставки')

    payment_method = models.CharField(max_length=2,
                                      choices=Payment.choices,
                                      default=Payment.ON_DELIVERY,
                                      verbose_name='Спосіб оплати')
 
    paid = models.BooleanField(default=False, verbose_name='Оплачено')
    liqpay_id = models.CharField(max_length=250, blank=True, null=True)
    monobank_id = models.CharField(max_length=250, blank=True, null=True)
 
    comment = models.TextField(max_length=500, blank=True,
                               verbose_name='Коментар клієнта')

    created = models.DateTimeField(auto_now_add=True, verbose_name='Створено')
    updated = models.DateTimeField(auto_now=True, verbose_name='Оновлено')
    user_uuid = models.UUIDField(verbose_name='Ідентифікатор покупця', blank=True, null=True)
    dont_callback = models.BooleanField(default=False, verbose_name='Не турбувати дзвінками')
    exported = models.BooleanField(default=False)
    passed_to_google = models.BooleanField(default=False, verbose_name='Передано в Google')

    class Meta:
        verbose_name = 'Замовлення'
        verbose_name_plural = 'Замовлення'
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created']),
            models.Index(fields=['status']),
            models.Index(fields=['user_uuid'])
        ]

    def __str__(self):
        return f'Замовлення {self.id}'


    def get_absolute_url(self):
        return reverse('admin:%s_%s_change' % (self._meta.app_label, self._meta.model_name), args=[self.id])

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())

    def clean_phone(self):
        digits = re.sub(r'\D', '', self.phone)  # видаляємо все, крім цифр

        # Якщо номер починається з '0' -> замінюємо на '38'
        if digits.startswith('0'):
            digits = '38' + digits
        # Якщо номер починається з '80' -> замінюємо на '3' + ...
        elif digits.startswith('80'):
            digits = '3' + digits
        # Якщо номер починається з '96', '97' і т.д. — додаємо '380'
        elif len(digits) == 9:
            digits = '380' + digits
        # Якщо номер починається з '+' — вже може бути ок
        elif digits.startswith('380'):
            pass
        else:
            # fallback або виняток
            digits = digits  # або raise ValidationError("Некоректний номер телефону")

        return digits


class OrderItem(models.Model):
    order = models.ForeignKey(Order,
                              related_name='items',
                              on_delete=models.CASCADE,
                              verbose_name='Замовлення')
    product = models.ForeignKey(Product,
                                related_name='order_items',
                                on_delete=models.PROTECT,
                                verbose_name='Товар')
    price = models.PositiveIntegerField(verbose_name='Ціна')
    quantity = models.PositiveIntegerField(default=1, verbose_name='Кількість')

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товари'

    def __str__(self):
        return str(self.id)

    def get_cost(self):
        return self.price * self.quantity


class OrderOneClick(models.Model):
    class Status(models.TextChoices):
        NEW = 'nw', 'Нова заявка'
        DONE = 'cd', 'Опрацьовано'
    status = models.CharField(max_length=2, choices=Status.choices, 
                              default=Status.NEW, verbose_name='Статус')
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                blank=True, null=True, verbose_name='Товар')

    order = models.OneToOneField(Order, on_delete=models.CASCADE, blank=True, 
                                 null=True, verbose_name='Замовлення')
    phone = models.CharField(max_length=100, verbose_name='Телефон')

    created = models.DateTimeField(auto_now_add=True, verbose_name='Створено')

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Замовлення в 1 клік'
        verbose_name_plural = 'Замовлення в 1 клік'
    
    def __str__(self):
        return f'Замовлення #{self.id}'
