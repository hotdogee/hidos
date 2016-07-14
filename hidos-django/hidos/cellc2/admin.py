from django.contrib import admin

from cell.admin import TaskAdmin

from .models import Task

admin.site.register(Task, TaskAdmin)
