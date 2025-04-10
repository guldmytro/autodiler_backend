from shop.models import Category
from slugify import slugify
import uuid



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
        if not source_id or not name or len(str(item.source_id)) < 5:
            break

        if parent is None:
            category, _ = Category.objects.get_or_create(
                source_id=source_id,
                defaults={'name_ua': name, 'name_ru': name, 
                          'slug': generate_slug(name)}
            )
        else:
            try:
                category = parent.get_children().get(source_id=source_id)
            except Category.DoesNotExist:
                category = parent.add_child(
                    source_id=source_id,
                    name_ua=name,
                    name_ru=name,
                    slug=generate_slug(name)
                )
        parent = category

    return category