# Generated by Django 5.0.1 on 2024-03-19 13:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0004_alter_product_image_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='image_source',
            field=models.URLField(blank=True, null=True, verbose_name='Посилання на оригінальну картинку'),
        ),
    ]