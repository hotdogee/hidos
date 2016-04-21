from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from app.models import Folder, ImageAnalysis


class Task(ImageAnalysis):
    number_of_ovum = models.IntegerField(null=True)
    number_of_A = models.IntegerField(null=True)
    number_of_B = models.IntegerField(null=True)
    number_of_C = models.IntegerField(null=True)
    number_of_D = models.IntegerField(null=True)
    number_of_E = models.IntegerField(null=True)
    mother_name = models.CharField(max_length=32,null=True)
    description = models.CharField(max_length=32,null=True)

    def __unicode__(self):
        return self.task_id

    def get_absolute_url(self):
        return reverse('icsi:retrieve', args=[str(self.task_id)])

    class Meta:
        verbose_name = 'Image Analysis'

class Ovum(models.Model):
    ovum_id = models.CharField(max_length=32, primary_key=True)
    ovum_number = models.IntegerField(null=True)
    parent_imageanalysis = models.ForeignKey('Task',related_name = 'ovums', null = True)
    grade = models.CharField(max_length=32, default='A')
    graded_time = models.DateTimeField(null=True)
    label_grade = models.CharField(max_length=32, null=True)
    archived = models.BooleanField()



# TODO: Permissions class for sharing

