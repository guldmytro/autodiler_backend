from django.contrib import admin
from seo.models import SeoItem
from ckeditor.widgets import CKEditorWidget
from django.db import models


@admin.register(SeoItem)
class SeoItemAdmin(admin.ModelAdmin):
    list_display = ['link']
    search_fields = ['link']
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget}
    }
