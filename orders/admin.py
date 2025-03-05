from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'status', 'first_name', 'last_name', 'email',
                    'phone', 'delivery', 'paid', 'created', 'updated']
    list_filter = ['status', 'paid', 'liqpay_id', 'created', 'updated']
    inlines = [OrderItemInline]
