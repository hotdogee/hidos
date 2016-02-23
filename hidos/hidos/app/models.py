from django.db import models 
from django.contrib.auth.models import User

class Folder(models.Model):
    folder_id = models.CharField(max_length=32, primary_key=True)
    name = models.CharField(max_length=255) # display name
    owner = models.ForeignKey(User, models.CASCADE)
    parent_folder = models.ForeignKey('self', models.CASCADE, related_name='child_folders')
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
	abstract = True

class ImageAnalysis(models.Model):
    task_id = models.CharField(max_length=32, primary_key=True) # ex. 128c8661c25d45b8-9ca7809a09619db9
    enqueue_date = models.DateTimeField(auto_now_add=True)
    dequeue_date = models.DateTimeField(null=True)
    result_date = models.DateTimeField(null=True)
    result_status = models.CharField(max_length=32, default='queued') # queued, running, success, failed
    user = models.ForeignKey(User, null=True)
    # parent_folder = models.ForeignKey(Folder, models.SET_NULL, null=True)
    version = models.CharField(max_length=32)
    user_filename = models.CharField(max_length=255) # ext3 max filename = 255

    class Meta:
	abstract = True


