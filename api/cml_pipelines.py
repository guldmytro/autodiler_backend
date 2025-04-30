# -*- coding: utf-8 -
"""
This file was generated with the cmlpipelines management command.
It contains the pipelines classes for that accept or send items for
import/export purposes.

To activate your pipelines add the following to your settings.py:
    CML_PROJECT_PIPELINES = 'backend.cml_pipelines'
"""

import decimal
from cml.items import Order, OrderItem
import orders.models as prod
from shop.models import Product
import logging
from shop.models import *
from .utils import get_or_create_category_tree, generate_slug, upload_image
from orders.models import Order


logger = logging.getLogger(__name__)


class GroupPipeline(object):
    """
    Item fields:
    id
    name
    groups
    """
    def process_item(self, item):
        pass


class PropertyPipeline(object):
    """
    Item fields:
    id
    name
    value_type
    for_products
    """
    def process_item(self, item):
        pass


class PropertyVariantPipeline(object):
    """
    Item fields:
    id
    value
    property_id
    """
    def process_item(self, item):
        pass


class SkuPipeline(object):
    """
    Item fields:
    id
    name
    name_full
    international_abbr
    """
    def process_item(self, item):
        pass


class TaxPipeline(object):
    """
    Item fields:
    name
    value
    """
    def process_item(self, item):
        pass


class ProductPipeline(object):
    """
    Item fields:
    id
    name
    sku_id
    group_ids
    properties
    tax_name
    image_path
    additional_fields

    Avtodiler fields:
    name
    name_ru
    sku
    vin
    producer
    params
    params_ru
    desc
    desc_ru
    g1_id
    g1_name
    g2_id
    g2_name
    g3_id
    g3_name
    """
    def process_item(self, item):
        logger.info(f'Завантаження товару {item.sku} ID= {item.id}')
        if item.sku == '16075':
            logger.debug(f'{item.sku} has 1c group id 1: {item.g1_id}')
            logger.debug(item.g2_id)
            logger.debug(item.g3_id)

        try:
            product_obj = Product.objects.get(sku=item.sku)
        except Product.DoesNotExist:
            slug = generate_slug(item.name or item.name_ru)
            product_obj = Product(sku=item.sku, slug=slug)
            product_obj.price = 0
            product_obj.quantity = 0
        
        if product_obj.slug is None:
            product_obj.slug = generate_slug(item.name or item.name_ru)
        
        if product_obj.id_1c is None:
            product_obj.id_1c = item.id
        
        product_obj.set_current_language('uk')

        product_obj.name = item.name or item.name_ru
        product_obj.description = item.desc or item.desc_ru

        product_obj.set_current_language('ru')
        product_obj.name = item.name_ru or item.name
        product_obj.description = item.desc_ru or item.desc

        product_obj.producer = item.producer
        product_obj.vin = item.vin
        
        
        try:
            c = get_or_create_category_tree(item)
            product_obj.category = c
        except Exception as e:
            logger.error(f'Category creating error for product with sku {item.sku}: {e}')
        try:
            product_obj.full_clean()
            product_obj.save()
            if not product_obj.image:
                upload_image(f'https://imidgauto.bigbrain.com.ua:27015/Foto/{item.sku}-01.jpg', 
                            product_obj)
        except Exception as e:
            logger.error(f'Product saving error for {item.sku}: {e}')
        return item


class PriceTypePipeline(object):
    """
    Item fields:
    id
    name
    currency
    tax_name
    tax_in_sum
    """
    def process_item(self, item):
        pass


class OfferPipeline(object):
    """
    Item fields:
    id
    name
    sku_id
    prices
    code_1c
    """
    def process_item(self, item):

        sku = item.code_1c

        try:
            p = Product.objects.get(sku=sku)
            try:
                quantity = int(item.quantity)
                if quantity < 0:
                    quantity = 0
                if p.quantity != quantity:
                    p.quantity = quantity
                    p.save()
            except:
                pass
            
            if len(item.prices) > 0:
                try:
                    new_price = int(item.prices[0].price_for_sku)
                    if p.price != new_price:
                        p.price = new_price
                        p.save()
                except:
                    pass
            logger.info(f'Offer successfully updated for product {sku} (price = {p.price}, quantity = {p.quantity})')
        except Product.DoesNotExist:
            logger.warning(f'Offer with sku {sku} not found')
            pass
        
        return item


class OrderPipeline(object):
    """
    Item fields:
    id
    number
    date
    currency_name
    currency_rate
    operation
    role
    sum
    client
    time
    comment
    items
    additional_fields
    """
    def process_item(self, item):
        return {
            'id': item.id,
            'number': item.id,
            
        }

    def yield_item(self):
        for order in Order.objects.all():
            yield order

    def flush(self):
        pass
