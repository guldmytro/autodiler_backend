# Generated by Django 5.0.1 on 2025-05-05 10:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0009_alter_order_user_uuid_alter_orderoneclick_created_and_more'),
        ('shop', '0018_product_id_1c'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderoneclick',
            name='product',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='shop.product', verbose_name='Товар'),
        ),
    ]
