from django.contrib import admin

from .models import File

class FileAdmin(admin.ModelAdmin):
    date_hierarchy = 'modified'
    fields = ('id', 'owner', 'folder', 'name', 'type', 'content_type', 'content_id',
            'created', 'modified')
    readonly_fields = ('id', 'created', 'modified')
    search_fields = ['id', 'owner', 'type', 'name']
    list_filter = ('owner', 'content_type')
    list_display = ('__unicode__', 'type', 'folder', 'owner', 'modified')

admin.site.register(File, FileAdmin)