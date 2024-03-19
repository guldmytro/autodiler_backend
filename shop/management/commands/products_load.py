from django.core.management import BaseCommand
import csv
import requests
import json
from shop.models import Product, Category
from django.core.files.base import ContentFile


class Command(BaseCommand):
    help = 'Parse product.csv and load it into the database'
    products = []
    csvfile = 'products.csv'

    def handle(self, *args, **options):
        self.parse_csv_file()
        self.load_products()

    def parse_csv_file(self):
        """
        Uses self.csvfile and save data to self.products attribute
        :return: None
        """
        with open(self.csvfile, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Copy keys before iterations
                keys = list(row.keys())
                # Create a new list of params
                params = []
                for key in keys:
                    if key.startswith('param_name-'):
                        param_num = key.split('-')[
                            -1]  # Get param number
                        param_units = row.get(f'param_units-{param_num}', '')
                        param_value = row.get(f'param_value-{param_num}', '')
                        if row[key] and param_value:
                            # Add param to list of params
                            params.append({
                                'name': row[key],
                                'units': param_units,
                                'value': param_value
                            })
                        # Delete params from main dict
                        del row[f'param_name-{param_num}']
                        del row[f'param_units-{param_num}']
                        del row[f'param_value-{param_num}']

                # Add params to product dict
                row['params'] = params
                self.products.append(row)

    def load_products(self):
        """
        Loop self.products
        :return: None
        """
        cnt = 0
        for product in self.products:
            cnt += 1
            print(cnt)
            sku = product.get('sku')
            if sku is None:
                continue

            name_ru = product.get('name')
            name_ua = product.get('name_ua')
            if name_ru is None and name_ua is None:
                continue

            try:
                product_obj = Product.objects.get(sku=sku)
            except Product.DoesNotExist:
                product_obj = Product(sku=sku)
            product_obj.set_current_language('uk')
            product_obj.name = name_ua or name_ru
            product_obj.search_query = product.get('search_query_ua') \
                or product.get('search_query')
            product_obj.description = product.get('description_ua') \
                or product.get('description')
            product_obj.set_current_language('ru')
            product_obj.name = name_ru or name_ua
            product_obj.search_query = product.get('search_query') \
                or product.get('search_query_ua')
            product_obj.description = product.get('description') \
                or product.get('description_ua')
            product_obj.price = int(product.get('price', 0)) \
                if product.get('price', '') != '' else 0
            product_obj.quantity = int(product.get('quantity', 0)) \
                if product.get('quantity', '') != '' else 0
            product_obj.producer = product.get('producer', '').strip()
            product_obj.country = product.get('country', '').strip()
            group_source_id = int(product.get('group_id', None))
            if group_source_id is not None:
                try:
                    cat = Category.objects.get(source_id=group_source_id)
                    product_obj.category = cat
                except Category.DoesNotExist:
                    print(f'category {group_source_id} does not exist')
            product_obj.params = product.get('params')
            try:
                product_obj.image_source = product.get('image_link')
                product_obj.full_clean()
            except:
                product_obj.image_source = None
            if product_obj.image is None:
                self.upload_image(product.get('image_link'), product_obj)
            product_obj.full_clean()
            product_obj.save()

    def upload_image(self, url, product_obj):
        if url is None:
            return None
        try:
            response = requests.get(url)
        except requests.exceptions.ConnectionError:
            response = requests.get(url)
        image_name = url.split('/')[-1][:300]
        if response.status_code == 200:
            product_obj.image.save(image_name, ContentFile(response.content),
                                   save=True)
        else:
            print(f'Failed to download {url}')





