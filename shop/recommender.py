import redis
from django.conf import settings
from .models import Product
from django.db.models.functions import Concat
from django.db.models import Value, CharField
from django.conf import Settings


r = redis.Redis(host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB)


class Recommender:
    def get_product_key(self, id):
        return f'product:{id}:purchased_with'

    def products_bought(self, products):
        products_ids = [p.id for p in products]
        for product_id in products_ids:
            for with_id in products_ids:
                if product_id != with_id:
                    r.zincrby(self.get_product_key(product_id),
                              1,
                              with_id)

    def suggest_products_for(self, products, max_results=6, request=None):
        lang = request.LANGUAGE_CODE
        absolute_url = request.build_absolute_uri(settings.MEDIA_URL)
        products_ids = [p.id for p in products]
        if len(products_ids) == 1:
            suggestions = r.zrange(
                self.get_product_key(products_ids[0]),
                0, -1, desc=True
            )[:max_results]
        else:
            flat_ids = ''.join([str(id) for id in products_ids])
            tmp_key = f'tmp{flat_ids}'
            keys = [self.get_product_key(id) for id in products_ids]
            r.zunionstore(tmp_key, keys)
            r.zrem(tmp_key, *products_ids)
            suggestions = r.zrange(tmp_key, 0, -1,
                                   desc=True)[:max_results]
            r.delete(tmp_key)
        suggested_products_ids = [int(id) for id in suggestions]
        suggested_products = list(Product.objects.filter(
            id__in=suggested_products_ids,
            translation__language_code=lang
        ).annotate(
            image_src=Concat(
                Value(absolute_url),
                'image',
                output_field=CharField()
            )
        ).values(
            'id', 'translation__name', 'slug',
            'price', 'image_src', 'sku', 'quantity'
            )
        )

        suggested_products.sort(
            key=lambda x: suggested_products_ids.index(x['id']))
        return suggested_products
