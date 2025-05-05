from django.contrib import admin
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory
from parler.admin import TranslatableAdmin
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(TreeAdmin, TranslatableAdmin):
    form = movenodeform_factory(Category)
    search_fields = ['name_ua', 'name_ru']


@admin.register(Product)
class ProductAdmin(TranslatableAdmin):
    list_select_related = ['category']
    search_fields = ['sku', 'translation__name']

