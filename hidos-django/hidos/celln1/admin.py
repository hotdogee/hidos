from django.contrib import admin

from .models import CellN1Task

@admin.register(CellN1Task)
class CellATaskAdmin(admin.ModelAdmin):
    date_hierarchy = 'modified'
    fields = ('task_id', 'status', 'user', 'parent_folder', 'version',
            'cell_body','outgrowth_length','mean_length',
            'number_of_branches','mean_branch','neurite_outgrowth',
            'mean_outgrowth',
            'uploaded_filename', 'uploaded_filetype', 'stdout', 'stderr',
            'dequeued', 'finished',
            'created', 'modified')
    readonly_fields = ('created', 'modified')
    search_fields = ['task_id', 'status', 'user', 'uploaded_filename']
    view_on_site = True
    list_display = ('__unicode__', 'status', 'user', 'modified', 'original_image')
    list_filter = ('status','user')
