from shop.models import Category
from slugify import slugify
import uuid
from django.core.files.base import ContentFile
import requests
import logging

logger = logging.getLogger(__name__)


def generate_slug(text):
    if not text:
        return None
    uuid_str = str(uuid.uuid4()).split('-')[0]
    return f'{slugify(text)}-{uuid_str}'

def get_or_create_category_tree(item):
    parent = None
    levels = [
        (item.g1_id, item.g1_name),
        (item.g2_id, item.g2_name),
        (item.g3_id, item.g3_name),
    ]

    for source_id, name in levels:
        if not source_id or not name or len(str(source_id)) < 5:
            break

        if parent is None:
            # Пошук серед кореневих елементів
            category = Category.get_root_nodes().filter(source_id=source_id).first()
            if not category:
                category = Category.add_root(
                    source_id=source_id,
                    name_ua=name,
                    name_ru=name,
                    slug=generate_slug(name)
                )
        else:
            # Дочірній елемент
            category = parent.get_children().filter(source_id=source_id).first()
            if not category:
                category = parent.add_child(
                    source_id=source_id,
                    name_ua=name,
                    name_ru=name,
                    slug=generate_slug(name)
                )

        parent = category

    return category
    

def upload_image(url, product_obj):
    if url is None:
        return None

    # Проверка, не загружалось ли уже изображение для этого URL
    image_name = url.split('/')[-1][:300]

    try:
        response = requests.get(url)
        response.raise_for_status()  # Проверка на успешный ответ (status_code 200)
    except:
        logger.error(f'Failed to download image from {url}')
        return None

    if response.status_code == 200:
        product_obj.image.save(image_name, ContentFile(response.content), save=True)
        logger.info(f'Image uploaded successfully for product {product_obj.sku}')
    else:
        logger.error(f'Failed to download image from {url}, HTTP status code: {response.status_code}')


def upload_images(product_obj):
    for i in range(4):
        if i == 0:
            continue
        url = f'https://imidgauto.bigbrain.com.ua:27015/Foto/{product_obj.sku}-0{i+1}.jpg'

        # Проверка, не загружалось ли уже изображение для этого URL
        image_name = url.split('/')[-1][:300]

        try:
            response = requests.get(url)
            response.raise_for_status()  # Проверка на успешный ответ (status_code 200)
        except:
            logger.error(f'Failed to download image from {url}')
            continue

        if response.status_code == 200:
            print(response.status_code)
            if i + 1 == 1:
                product_obj.image.save(image_name, ContentFile(response.content), save=True)
                logger.info(f'Image uploaded successfully for product {product_obj.sku}')
            if i + 1 == 2:
                product_obj.image2.save(image_name, ContentFile(response.content), save=True)
                logger.info(f'Image uploaded successfully for product {product_obj.sku}')
            if i + 1 == 3:
                product_obj.image3.save(image_name, ContentFile(response.content), save=True)
                logger.info(f'Image uploaded successfully for product {product_obj.sku}')
            if i + 1 == 4:
                product_obj.image3.save(image_name, ContentFile(response.content), save=True)
                logger.info(f'Image uploaded successfully for product {product_obj.sku}')
        else:
            logger.error(f'Failed to download image from {url}, HTTP status code: {response.status_code}')