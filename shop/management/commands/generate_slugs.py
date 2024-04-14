from django.core.management import BaseCommand
from shop.models import Product, Category
from slugify import slugify
import uuid


class Command(BaseCommand):
    help = 'Looping all products and terms and generate slug for items without slug'

    def handle(self, *args, **options):
        self.loop_items()

    def loop_items(self):
        for p in Product.objects.all():
            if p.slug:
                pass
            else:
                p.set_current_language('uk')
                uuid_str = str(uuid.uuid4()).split('-')[0]
                p.slug = f'{slugify(p.name)}-{uuid_str}'
                p.save()

        for c in Category.objects.all():
            if c.slug:
                pass
            else:
                uuid_str = str(uuid.uuid4()).split('-')[0]
                c.slug = f'{slugify(c.name_ua)}-{uuid_str}'
                c.save()
