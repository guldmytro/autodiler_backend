# Generated by Django 5.0.1 on 2025-04-10 09:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0016_alter_category_slug_alter_product_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='params',
            field=models.JSONField(blank=True, null=True, verbose_name='Параметри'),
        ),
    ]
