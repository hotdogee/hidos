from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from django_extensions.db.models import TimeStampedModel


class Folder(TimeStampedModel):
    folder_id = models.CharField(max_length=32, primary_key=True)
    name = models.CharField(max_length=255) # display name
    owner = models.ForeignKey(User, models.CASCADE)
    parent_folder = models.ForeignKey('self', models.CASCADE, related_name='child_folders')


# Abstract model for a user submitted task
class TaskModel(TimeStampedModel):
    task_id = models.CharField(max_length=32, primary_key=True) # ex. 128c8661c25d45b8-9ca7809a09619db9
    status = models.CharField(max_length=32, default='queued') # queued, running, success, failed
    dequeued = models.DateTimeField(null=True, blank=True)
    finished = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(User, null=True, blank=True)
    parent_folder = models.ForeignKey(Folder, models.SET_NULL, null=True, blank=True)
    version = models.CharField(max_length=32)
    #cell_ratio = models.FloatField()

    def __unicode__(self):
        return self.task_id

    class Meta(TimeStampedModel.Meta):
        abstract = True


# CellQ result model
class CellTaskModel(TaskModel):
    # user file name
    user_filename = models.CharField(max_length=255) # ext3 max filename = 255
    # uploaded image file type
    uploaded_type = models.CharField(max_length=10)
    stdout = models.TextField(blank=True)
    stderr = models.TextField(blank=True)

    def __unicode__(self):
        return '{0} ({1})'.format(self.user_filename, self.task_id[:6])

    class Meta(TaskModel.Meta):
        abstract = True

# TODO: Permissions class for sharing
