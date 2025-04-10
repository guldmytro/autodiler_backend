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
        logger.info(f'Завантаження товару:')
        logger.info(f'name: {item.name}')
        logger.info(f'name_ru: {item.name_ru}')
        logger.info(f'sku: {item.sku}')
        logger.info(f'vin: {item.vin}')
        logger.info(f'producer: {item.producer}')
        logger.info(f'params: {item.params}')
        logger.info(f'params_ru: {item.params_ru}')
        logger.info(f'desc: {item.desc}')
        logger.info(f'desc_ru: {item.desc_ru}')
        logger.info(f'g1_id: {item.g1_id}')
        logger.info(f'g1_name: {item.g1_name}')
        logger.info(f'g2_id: {item.g2_id}')
        logger.info(f'g2_name: {item.g2_name}')
        logger.info(f'g3_id: {item.g3_id}')
        logger.info(f'g3_name: {item.g3_name}')
        pass


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
        except Product.DoesNotExist:
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
        pass

    def yield_item(self):
        pass

    def flush(self):
        pass
