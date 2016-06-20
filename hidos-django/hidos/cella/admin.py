from django.contrib import admin
from .models import CellATask

@admin.register(CellATask)
class CellATaskAdmin(admin.ModelAdmin):
    date_hierarchy = 'modified'
    fields = ('task_id', 'status', 'user', 'parent_folder', 'version',
            'extremity','junction','mesh','total_branch_length','total_segment_length','total_network_length','total_mesh_area',
            'uploaded_filename', 'uploaded_filetype', 'stdout', 'stderr',
            'dequeued', 'finished',
            'created', 'modified')
    readonly_fields = ('created', 'modified')
    search_fields = ['task_id', 'status', 'user', 'uploaded_filename']
    view_on_site = True
    list_display = ('__unicode__', 'status', 'user', 'modified', 'original_image')
    list_filter = ('status','user')
