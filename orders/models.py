from django.db import models
from shop.models import Product
from django.contrib.auth.models import User
from django.urls import reverse


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
    phone = models.CharField(max_length=17, verbose_name='Телефон')
    email = models.EmailField(verbose_name='E-mail')

    delivery = models.CharField(max_length=2,
                                choices=Delivery.choices,
                                default=Delivery.PICKUP,
                                verbose_name='Спосіб доставки')
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
    user_uuid = models.UUIDField(verbose_name='Ідентифікатор покупця')

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
