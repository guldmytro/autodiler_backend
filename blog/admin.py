from django.contrib import admin
from .models import Post
from parler.admin import TranslatableAdmin
from django.db import models
from ckeditor.widgets import CKEditorWidget


@admin.register(Post)
class PostAdmin(TranslatableAdmin):
    list_display = ['title', 'created', 'updated']
    list_filter = ['created']
    search_fields = ['title', 'body']
    ordering = ['-created']
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget}
    }
