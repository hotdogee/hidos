from django.contrib import admin

class TaskAdmin(admin.ModelAdmin):
    date_hierarchy = 'modified'
    fields = ('id', 'status', 'owner', 'parent_folder', 'version',
            'result',
            'name', 'uploaded_filetype', 'stdout', 'stderr',
            'dequeued', 'finished',
            'created', 'modified')
    readonly_fields = ('created', 'modified')
    search_fields = ['id', 'status', 'owner', 'name']
    view_on_site = True
    list_display = ('__unicode__', 'result', 'status', 'owner', 'modified')