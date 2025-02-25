from django.contrib import admin
from .models import Output


@admin.register(Output)
class FaqAdmin(admin.ModelAdmin):
    list_display = ['id', 'file', 'created']