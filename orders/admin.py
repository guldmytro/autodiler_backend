from django.contrib import admin
from .models import Order, OrderItem, OrderOneClick
from django.utils.html import format_html
from django.urls import reverse
from django.utils.translation import gettext_lazy as _



class HasUtmFilter(admin.SimpleListFilter):
    title = _('UTM мітки')
    parameter_name = 'has_utm'

    def lookups(self, request, model_admin):
        return (
            ('yes', ('Так')),
            ('no', ('Ні')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.exclude(utm__isnull=True).exclude(utm__exact='')
        if self.value() == 'no':
            return queryset.filter(utm__isnull=True) | queryset.filter(utm__exact='')
        return queryset


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']
    autocomplete_fields = ['product']
    extra = 1
    
    readonly_fields = ['product_link']  # Add the custom link as readonly

    def product_link(self, obj):
        if obj.product:
            url = reverse('admin:shop_product_change', args=[obj.product.id])
            return format_html('<a href="{}" target="_blank">{}</a>', url, 'Посилання на товар')
        return "-"
    product_link.short_description = 'Переглянути товар'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'status', 'first_name', 'last_name', 'email',
                    'phone', 'delivery', 'paid', 'created', 'updated']
    list_filter = ['status', 'paid', 'dont_callback', HasUtmFilter, 'created', 'updated']
    inlines = [OrderItemInline]

@admin.register(OrderOneClick)
class OrderOneClickAdmin(admin.ModelAdmin):
    list_display = ['id', 'status', 'phone', 'product_link', 'order_link', 'created']
    list_display_links = ['id',]
    list_editable = ['status',]
    list_filter = ['status', 'created']

    readonly_fields = ['order_link', 'product', 'product_link']
    def order_link(self, obj):
        if obj.order:
            url = reverse('admin:orders_order_change', args=[obj.order.id])
            return format_html('<a href="{}" target="_blank">{}</a>', url, obj.order)
        return "-"
    order_link.short_description = 'Замовлення'

    def product_link(self, obj):
        if obj.product:
            url = reverse('admin:shop_product_change', args=[obj.product.id])
            return format_html('<a href="{}" target="_blank">{}</a>', url, obj.product)
        return "-"
    product_link.short_description = 'Товар'
