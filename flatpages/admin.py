from rocksoc.flatpages.models import FlatPage
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

class FlatPageOptions(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('url', 'title', 'format', 'content', 'sites')}),
        ('Advanced options', {'classes': ('collapse',), 'fields': ('enable_comments', 'registration_required', 'template_name')}),
    )
    list_filter = ('sites',)
    search_fieldsets = ('url', 'title')

admin.site.register(FlatPage, FlatPageOptions)

