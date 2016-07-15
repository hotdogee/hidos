from django.contrib import admin

from .models import CellM1Task

@admin.register(CellM1Task)
class CellATaskAdmin(admin.ModelAdmin):
    date_hierarchy = 'modified'
    fields = ('task_id', 'status', 'user', 'parent_folder', 'version',
              'feedback_satisfied', 'feedback_opinions',
            'cell_count',
            'uploaded_filename', 'uploaded_filetype', 'stdout', 'stderr',
            'dequeued', 'finished',
            'created', 'modified')
    readonly_fields = ('created', 'modified')
    search_fields = ['task_id', 'status', 'user', 'uploaded_filename']
    view_on_site = True
    list_display = ('__unicode__', 'status', 'user', 'modified', 'original_image','feedback_satisfied', 'feedback_opinions')
    list_filter = ('status','user','feedback_satisfied')
