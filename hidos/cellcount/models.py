from django.db import models
from django.core.urlresolvers import reverse
from app.models import Folder, ImageAnalysis


class CellcountFolder(Folder):
    method = models.CharField(max_length=32,default='Cellcount')

# CellQ result model
class CellcountImageAnalysis(ImageAnalysis):
    result = models.TextField(blank=True)

    def __unicode__(self):
        return self.task_id

    def get_absolute_url(self):
        return reverse('cellcount:retrieve', args=[str(self.task_id)])

    class Meta:
        verbose_name = 'Image Analysis'

# TODO: Permissions class for sharing