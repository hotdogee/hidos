from django.contrib import admin

from .models import CellC2Task

class CellC2TaskAdmin(admin.ModelAdmin):
    date_hierarchy = 'modified'
    fields = ('task_id', 'status', 'user', 'parent_folder', 'version',
            'cell_ratio', 'count_min', 'count_max',
            'uploaded_filename', 'uploaded_filetype', 'stdout', 'stderr',
            'dequeued', 'finished',
            'created', 'modified')
    readonly_fields = ('created', 'modified')
    search_fields = ['task_id', 'status', 'user', 'uploaded_filename']
    view_on_site = True
    list_display = ('__unicode__', 'cell_ratio', 'status', 'user', 'modified')

admin.site.register(CellC2Task, CellC2TaskAdmin)
