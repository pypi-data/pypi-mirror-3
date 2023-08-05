from __future__ import absolute_import

from django.conf import settings
from django.contrib import admin

from .models import FieldHelp, use_database


class FieldHelpAdmin(admin.ModelAdmin):
    fields=('help_text',)
    list_display=('app_title', 'model_title', 'field_title', 'help_text')
    list_display_links=('field_title',)
    list_filter=('content_type',)
    search_fields=('field_name', 'help_text')
                

if use_database():
    admin.site.register(FieldHelp, FieldHelpAdmin)
