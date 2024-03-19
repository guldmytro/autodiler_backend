from django.contrib import admin
from parler.admin import TranslatableAdmin
from .models import Faq


@admin.register(Faq)
class FaqAdmin(TranslatableAdmin):
    list_display = ['question']
