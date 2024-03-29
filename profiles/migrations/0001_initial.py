# Generated by Django 5.0.1 on 2024-03-19 06:36

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(blank=True, max_length=100, verbose_name="Ім'я")),
                ('last_name', models.CharField(blank=True, max_length=100, verbose_name='Прізвище')),
                ('phone', models.CharField(blank=True, max_length=25, verbose_name='Телефон')),
                ('delivery', models.CharField(blank=True, max_length=2, verbose_name='Доставка')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Створено')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Користувач')),
            ],
            options={
                'ordering': ['-created'],
            },
        ),
    ]
