from django.contrib import admin
from .models import CellATask

@admin.register(CellATask)
class CellATaskAdmin(admin.ModelAdmin):
    date_hierarchy = 'modified'
    fields = ('task_id', 'status', 'user', 'parent_folder', 'version',
            'feedback_satisfied', 'feedback_opinions',
            'extremity','junction','connectivity','total_network_length',
            'branch', 'total_branch_length', 'mean_branch_length','std_branch_length',
            'segment','total_segment_length','mean_segment_length', 'std_segment_length',
            'mesh','total_mesh_area','mean_mesh_area', 'std_mesh_area',
            'total_mesh_perimeter', 'mean_mesh_perimeter', 'std_mesh_perimeter',
            'uploaded_filename', 'uploaded_filetype', 'stdout', 'stderr',
            'dequeued', 'finished',
            'created', 'modified')
    readonly_fields = ('created', 'modified')
    search_fields = ['task_id', 'status', 'user', 'uploaded_filename']
    view_on_site = True
    list_display = ('__unicode__', 'status', 'user', 'modified', 'original_image',
                    'feedback_satisfied', 'feedback_opinions')
    list_filter = ('status','user','feedback_satisfied')
