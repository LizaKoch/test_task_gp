from django.contrib import admin
from loader.models import Document

class DocumentAdmin(admin.ModelAdmin):
    list_display = ('pk', 'status', 'row_count', 'document', 'created_at', 'updated_at')

admin.site.register(Document, DocumentAdmin)
