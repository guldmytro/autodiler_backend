# Generated by Django 5.0.1 on 2024-03-19 06:36

import django.db.models.deletion
import parler.fields
import parler.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('path', models.CharField(max_length=255, unique=True)),
                ('depth', models.PositiveIntegerField()),
                ('numchild', models.PositiveIntegerField(default=0)),
                ('source_id', models.PositiveIntegerField(unique=True, verbose_name='Ідентифікатор у                                                 вигрузці')),
                ('name_ua', models.CharField(max_length=200, verbose_name='Назва українською')),
                ('name_ru', models.CharField(max_length=200, verbose_name='Назва російською')),
                ('quantity', models.PositiveIntegerField(default=0, verbose_name='Кількість')),
                ('image', models.ImageField(blank=True, null=True, upload_to='terms/%Y/%m/%d/', verbose_name='Лого')),
            ],
            options={
                'verbose_name': 'Категорія',
                'verbose_name_plural': 'Категорії',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sku', models.CharField(max_length=10, unique=True, verbose_name='Артикул')),
                ('price', models.PositiveIntegerField(blank=True, verbose_name='Ціна')),
                ('image', models.ImageField(blank=True, upload_to='products/%Y/%m/%d/', verbose_name='Фото')),
                ('image_source', models.URLField(blank=True, verbose_name='Посилання на оригінальну картинку')),
                ('quantity', models.PositiveIntegerField(blank=True, verbose_name='Кількість')),
                ('producer', models.CharField(blank=True, max_length=50, verbose_name='Виробник')),
                ('country', models.CharField(blank=True, max_length=20, verbose_name='Країна виробник')),
                ('params', models.JSONField(blank=True, verbose_name='Параметри')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Створено')),
                ('category', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.PROTECT, related_name='products', to='shop.category', verbose_name='Категорія')),
            ],
            options={
                'verbose_name': 'Товар',
                'verbose_name_plural': 'Товари',
            },
            bases=(parler.models.TranslatableModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='ProductTranslation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(db_index=True, max_length=15, verbose_name='Language')),
                ('name', models.CharField(max_length=200, verbose_name='Назва')),
                ('search_query', models.CharField(blank=True, max_length=400, verbose_name='Пошукові фрази')),
                ('description', models.TextField(blank=True, verbose_name='Опис')),
                ('master', parler.fields.TranslationsForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='translation', to='shop.product')),
            ],
            options={
                'verbose_name': 'Товар Translation',
                'db_table': 'shop_product_translation',
                'db_tablespace': '',
                'managed': True,
                'default_permissions': (),
            },
            bases=(parler.models.TranslatedFieldsModelMixin, models.Model),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['sku'], name='shop_produc_sku_9aec58_idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['price'], name='shop_produc_price_3b79b5_idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['quantity'], name='shop_produc_quantit_2dfbef_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='producttranslation',
            unique_together={('language_code', 'master')},
        ),
    ]
