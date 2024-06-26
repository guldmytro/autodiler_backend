# Generated by Django 5.0.1 on 2024-04-27 07:41

import ckeditor_uploader.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SeoItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('link', models.URLField(help_text='Посилання повинно бути без / в кінці, та без get-параметрів', unique=True, verbose_name='Посилання')),
                ('title_tag', models.CharField(blank=True, max_length=500, verbose_name='<title>')),
                ('meta_description', models.CharField(blank=True, max_length=500, verbose_name='Meta-description')),
                ('content', ckeditor_uploader.fields.RichTextUploadingField(blank=True, verbose_name='Контент')),
            ],
            options={
                'verbose_name': 'Налаштування СЕО',
                'verbose_name_plural': 'Налаштування СЕО',
            },
        ),
    ]
