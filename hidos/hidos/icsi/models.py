from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from app.models import Folder, ImageAnalysis

class ICSIFolder(Folder):
    method = models.CharField(max_length=32,default='ICSI')

class ICSIImageAnalysis(ImageAnalysis):
    number_of_ovum = models.IntegerField(null=True)

    def __unicode__(self):
        return self.task_id

    def get_absolute_url(self):
        return reverse('icsi:retrieve', args=[str(self.task_id)])

    class Meta:
        verbose_name = 'Image Analysis'

class OvumGrade(models.Model):
    ovum_id = models.CharField(max_length=32, primary_key=True)
    ovum_number = models.IntegerField(null=True)
    parent_imageanalysis = models.ForeignKey('ICSIImageAnalysis',related_name = 'ovums', null = True)
    status = models.CharField(max_length=32, default='undefined')
    grade = models.CharField(max_length=32, default='A')
    graded_time = models.DateTimeField(null=True)
    



# TODO: Permissions class for sharing:q

