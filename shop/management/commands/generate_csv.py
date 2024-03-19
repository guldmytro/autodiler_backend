import csv
import os
from django.core.management import BaseCommand
from shop.models import Product
from django.conf import settings


class Command(BaseCommand):
    help = 'Generating csv-file of all products'

    def handle(self, *args, **options):
        products = Product.objects.all()
        export_dir = os.path.join(settings.MEDIA_ROOT, 'export')
        os.makedirs(export_dir, exist_ok=True)
        file_path = os.path.join(export_dir, 'export_uk.csv')
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            fields = ['sku', 'name', 'price']
            writer.writerow(fields)
            for product in products:
                product.set_current_language('uk')
                data_row = [str(getattr(product, field)) for field in fields]
                writer.writerow(data_row)
        file_path = os.path.join(export_dir, 'export_ru.csv')
        with open(file_path, 'w', newline='',
                  encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            fields = ['sku', 'name', 'price']
            writer.writerow(fields)
            for product in products:
                product.set_current_language('ru')
                data_row = [str(getattr(product, field)) for field in fields]
                writer.writerow(data_row)



