"""
Definition of models.
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from app.models import Folder

# CellC1 result model
class CellC1Analysis(models.Model):
    task_id = models.CharField(max_length=32, primary_key=True) # ex. 128c8661c25d45b8-9ca7809a09619db9
    enqueue_date = models.DateTimeField(auto_now_add=True)
    dequeue_date = models.DateTimeField(null=True)
    result = models.TextField(blank=True)
    result_outerr = models.TextField(blank=True)
    result_date = models.DateTimeField(null=True)
    result_status = models.CharField(max_length=32, default='queued') # queued, running, success, failed
    user = models.ForeignKey(User, null=True)
    parent_folder = models.ForeignKey(Folder, models.SET_NULL, null=True)
    version = models.CharField(max_length=32)
    user_filename = models.CharField(max_length=255) # ext3 max filename = 255
    #cell_ratio = models.FloatField()

    def __unicode__(self):
        return self.task_id

    def get_absolute_url(self):
        return reverse('cellc1:retrieve', args=[str(self.task_id)])

    class Meta:
        verbose_name = 'Cell C1 Analysis'

# TODO: Permissions class for sharing