from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .genericcollection import GenericCollectionTabularInline
from .settings import RELATION_MODELS, JAVASCRIPT_URL
from .forms import ArchivedpageForm
from .models import ArchivedPage, ArchivedFile

if RELATION_MODELS:
    from .models import ArchivedPageRelation

    class InlineRelation(GenericCollectionTabularInline):
        model = ArchivedPageRelation


class ArchivedPageAdmin(admin.ModelAdmin):
    form = ArchivedpageForm
    fieldsets = (
        (None, {'fields': ('url', 'original_url', 'title', 'content', )}),
        (_('Advanced options'), {'classes': ('collapse',), 'fields': ('metadata', 'template_name')}),
    )
    list_display = ('url', 'title')
    search_fields = ('url', 'title')

    if RELATION_MODELS:
        inlines = [InlineRelation, ]

    class Media:
        js = (JAVASCRIPT_URL + 'genericcollections.js',)


class ArchivedFileAdmin(admin.ModelAdmin):
    fields = ['original_url', 'content', ]
    list_display = ('original_url', )
    search_fields = ('original_url', )

admin.site.register(ArchivedPage, ArchivedPageAdmin)
admin.site.register(ArchivedFile, ArchivedFileAdmin)
