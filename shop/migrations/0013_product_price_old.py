# Generated by Django 5.0.1 on 2025-02-20 11:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0012_category_is_car_brand'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='price_old',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Ціна стара'),
        ),
    ]
