from django.core.management import BaseCommand
from shop.models import Category, Product


class Command(BaseCommand):
    help = 'Update terms quantity for each category'
    root_categories = []

    def handle(self, *args, **options):
        self.root_categories = Category.get_root_nodes()
        self.loop_root_categories()
        # self.clear_categories()

    def loop_root_categories(self):
        for root_category in self.root_categories:
            self.update_category_quantities(root_category)

    def update_category_quantities(self, category):
        """
        Функція для підрахунку кількості товарів (об'єктів Product) в
        категорії та всіх її підкатегоріях і оновлення поля quantity.
        """
        # Отримати кількість товарів у поточній категорії
        product_count = category.products.exclude(image__isnull=True).exclude(image='').filter(quantity__gt=0).count()

        # Отримати кількість товарів у всіх підкатегоріях
        subcategories = category.get_children()
        subcategories_count = 0
        for subcategory in subcategories:
            subcategories_count += self.update_category_quantities(subcategory)

        # Оновити кількість товарів для поточної категорії
        category.quantity = product_count + subcategories_count
        category.save()

        return product_count + subcategories_count

    def clear_categories(self):
        """
        Delete all empty cats
        :return: None
        """
        Product.objects.filter(image__isnull=True).delete()
        Product.objects.filter(image='').delete()
        Category.objects.filter(quantity=0).delete()
