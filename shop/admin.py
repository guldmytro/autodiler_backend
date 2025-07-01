from django.contrib import admin
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory
from parler.admin import TranslatableAdmin
from .models import Category, Product, Color
from django.utils.html import format_html


@admin.register(Category)
class CategoryAdmin(TreeAdmin, TranslatableAdmin):
    form = movenodeform_factory(Category)
    search_fields = ['name_ua', 'name_ru']


@admin.register(Product)
class ProductAdmin(TranslatableAdmin):
    list_select_related = ['category']
    search_fields = ['sku', 'translation__name']
    list_display = ['name', 'created', 'updated']
    list_filter = ['created', 'updated']
    autocomplete_fields = ['parent']



    

@admin.register(Color)
class ColorAdmin(TranslatableAdmin):
    list_display = ('name', 'hex_code', 'color_preview')
    search_fields = ('name', 'hex_code')

    def color_preview(self, obj):
        return format_html(
            '<div style="width: 30px; height: 20px; background-color: {}; border: 1px solid #000;"></div>',
            obj.hex_code
        )
    color_preview.short_description = 'Попередній перегляд'

