from shop.models import Category
from slugify import slugify
import uuid
from openai import OpenAI
from django.conf import settings



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
            try:
                category = Category.get_root_nodes().get(source_id=source_id)
            except Category.DoesNotExist:
                category = Category.add_root(
                    source_id=source_id,
                    name_ua=translate_with_chatgpt(name),
                    name_ru=name,
                    slug=generate_slug(name)
                )
        else:
            # Дочірній елемент
            try:
                category = parent.get_children().get(source_id=source_id)
            except Category.DoesNotExist:
                category = parent.add_child(
                    source_id=source_id,
                    name_ua=translate_with_chatgpt(name),
                    name_ru=name,
                    slug=generate_slug(name)
                )
        parent = category

    return category


client = OpenAI(api_key=settings.OPENAI_KEY)


def translate_with_chatgpt(text: str) -> str:
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful translator."},
                {"role": "user", "content": f"Translate the following text from Russian to Ukrainian:\n{text}"}
            ],
            temperature=0,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return text