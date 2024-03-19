# Generated by Django 5.0.1 on 2024-03-19 06:36

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('shop', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('nw', 'Нова заявка'), ('wk', 'У роботі'), ('ep', 'Комплектується'), ('dy', 'Доставляється'), ('wn', 'Чекає на складі нової пошти'), ('wp', 'Чекає в точці самовивозу'), ('dn', 'Виконано'), ('cl', 'Скасовано')], default='nw', max_length=2, verbose_name='Статус')),
                ('first_name', models.CharField(max_length=50, verbose_name="Ім'я")),
                ('last_name', models.CharField(max_length=50, verbose_name='Прізвище')),
                ('phone', models.CharField(max_length=17, verbose_name='Телефон')),
                ('email', models.EmailField(max_length=254, verbose_name='E-mail')),
                ('delivery', models.CharField(choices=[('nd', 'Нова пошта'), ('pu', 'Самовивіз')], default='pu', max_length=2, verbose_name='Спосіб доставки')),
                ('city', models.CharField(blank=True, max_length=255, verbose_name='Населений пункт')),
                ('nova_office', models.CharField(blank=True, max_length=255, verbose_name='Відділення Нової пошти')),
                ('payment_method', models.CharField(choices=[('od', 'При отриманні')], default='od', max_length=2, verbose_name='Спосіб оплати')),
                ('paid', models.BooleanField(default=False, verbose_name='Оплачено')),
                ('comment', models.TextField(blank=True, max_length=500, verbose_name='Коментар клієнта')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Створено')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Оновлено')),
                ('user_uuid', models.UUIDField(verbose_name='Ідентифікатор покупця')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='Користувач')),
            ],
            options={
                'verbose_name': 'Замовлення',
                'verbose_name_plural': 'Замовлення',
                'ordering': ['-created'],
            },
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.PositiveIntegerField(verbose_name='Ціна')),
                ('quantity', models.PositiveIntegerField(default=1, verbose_name='Кількість')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='orders.order', verbose_name='Замовлення')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='order_items', to='shop.product', verbose_name='Товар')),
            ],
            options={
                'verbose_name': 'Товар',
                'verbose_name_plural': 'Товари',
            },
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['-created'], name='orders_orde_created_743fca_idx'),
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['status'], name='orders_orde_status_c6dd84_idx'),
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['user_uuid'], name='orders_orde_user_uu_6e8cc0_idx'),
        ),
    ]
