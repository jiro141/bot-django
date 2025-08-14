from django.contrib import admin
from .models import KnowledgeBaseEntry

@admin.register(KnowledgeBaseEntry)
class KnowledgeBaseEntryAdmin(admin.ModelAdmin):
    list_display = ('title', 'tags', 'created_at')
    search_fields = ('title', 'content', 'tags')
    list_filter = ('created_at',)
