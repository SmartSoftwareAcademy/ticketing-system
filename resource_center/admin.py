from django.contrib import admin
from .models import *
# Register your models here.
from tinymce.widgets import TinyMCE


class IssuetAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
    )
    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()}
    }
    list_filter = (
        'title',
    )

    search_fields = ('title', 'content', 'id',)


admin.site.register(Issue, IssuetAdmin)
