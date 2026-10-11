from django.contrib import admin

class TaskAdmin(admin.ModelAdmin):
    date_hierarchy = 'modified'
    fields = ('id', 'status', 'progress', 'owner', 'folder', 'version',
            'result',
            'name', 'uploaded_filetype', 'error',
            'uploaded_image', 'result_image', 'uploaded_display', 'result_display',
            'dequeued', 'finished',
            'created', 'modified')
    readonly_fields = ('id', 'created', 'modified')
    search_fields = ['id', 'status', 'owner__email', 'name']
    list_filter = ('status',)
    view_on_site = True
    list_display = ('__str__', 'result', 'status', 'owner', 'modified')
