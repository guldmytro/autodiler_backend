from PIL import Image, ImageEnhance
from io import BytesIO
from django.core.files.base import ContentFile
from shop.models import Product
import os

def add_watermark_with_image(image_field, watermark_path='watermark.png', opacity=0.2):
    from PIL import Image, ImageEnhance
    from io import BytesIO
    from django.core.files.base import ContentFile

    # Відкриваємо зображення товару
    base_image = Image.open(image_field).convert("RGBA")
    base_width, base_height = base_image.size

    # Відкриваємо водяний знак
    watermark = Image.open(watermark_path).convert("RGBA")
    wm_width, wm_height = watermark.size

    # Масштабуємо з ефектом contain
    scale = min(base_width / wm_width, base_height / wm_height) * 0.5  # 50% від максимального розміру
    new_size = (int(wm_width * scale), int(wm_height * scale))
    watermark = watermark.resize(new_size, resample=Image.Resampling.LANCZOS)

    # Зменшуємо непрозорість
    alpha = watermark.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
    watermark.putalpha(alpha)

    # Створюємо прозорий шар тієї ж розмірності, що й основне зображення
    layer = Image.new("RGBA", base_image.size, (0, 0, 0, 0))

    # Обчислюємо позицію по центру
    x = (base_width - watermark.width) // 2
    y = (base_height - watermark.height) // 2

    # Розміщуємо водяний знак по центру
    layer.paste(watermark, (x, y), mask=watermark)

    # Накладаємо водяний знак
    watermarked = Image.alpha_composite(base_image, layer).convert("RGB")

    # Повертаємо як Django ContentFile
    buffer = BytesIO()
    watermarked.save(buffer, format='JPEG')
    return ContentFile(buffer.getvalue())

def test():
    image_fields = ['image', 'image2', 'image3', 'image4', 'image5']
    
    for product in Product.objects.all():
        print(product.pk)
        for field in image_fields:
            image = getattr(product, field)
            if image:
                watermarked = add_watermark_with_image(image)
                filename = os.path.basename(image.name)
                getattr(product, field).save(filename, watermarked, save=True)