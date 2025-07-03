from api.watermark import add_watermark_with_image
from django.core.management import BaseCommand
from shop.models import Product
from django.conf import settings
import os


class Command(BaseCommand):
    help = 'watermarking product'

    def handle(self, *args, **options):
        products = Product.objects.filter(watermarked=False, quantity__gt=0)[:150]
        image_fields = ['image', 'image2', 'image3', 'image4', 'image5']
    
        for product in products:
            for field in image_fields:
                image = getattr(product, field)
                if image:
                    watermarked = add_watermark_with_image(image)
                    filename = os.path.basename(image.name)
                    getattr(product, field).save(filename, watermarked, save=True)
            product.watermarked = True
            product.save()
        



