from __future__ import absolute_import, unicode_literals
import re
from os import path

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

from django_extensions.db.models import TimeStampedModel

from . import app_name, verbose_name, version

# class TimeStampedModel(models.Model):
#     """ TimeStampedModel
#     An abstract base class model that provides self-managed "created" and
#     "modified" fields.
#     """
#     created = CreationDateTimeField(_('created')) # editable=False, blank=True, auto_now_add=True
#     modified = ModificationDateTimeField(_('modified')) # auto_now_add=True

#     def save(self, **kwargs):
#         self.update_modified = kwargs.pop('update_modified', getattr(self, 'update_modified', True))
#         super(TimeStampedModel, self).save(**kwargs)

#     class Meta:
#         get_latest_by = 'modified'
#         ordering = ('-modified', '-created',)
#         abstract = True

folder_re = re.compile(r'^[^\\/:*?"<>|\.]+$', re.U)
file_re = re.compile(r'^[^\\/:*?"<>|]+$', re.U)

class Folder(TimeStampedModel):
    # id = models.AutoField(primary_key=True)
    id = models.CharField(max_length=32, primary_key=True) # ex. 128c8661c25d45b8-9ca7809a09619db9
    name = models.CharField(max_length=255,  # display name
        validators=[RegexValidator(folder_re, r'Folder names must not contain  \ / : * ? " < > | .')])
    owner = models.ForeignKey(User, models.CASCADE)
    parent_folder = models.ForeignKey('self', models.CASCADE, related_name='child_folders', null=True, blank=True)

    def __unicode__(self):
        return '{0} ({1})'.format(self.name, self.id[:6])

    @property
    def path(self): # will probably need some caching
        if not self.parent_folder:
            return self.name
        else:
            return self.parent_folder.path() + '/' + self.name

    class Meta(TimeStampedModel.Meta):
        pass

    # built in
    # def to_python(self, value): # CharField
    #     "Returns a Unicode object."
    #     if value in self.empty_values:
    #         return ''
    #     value = force_text(value)
    #     if self.strip:
    #         value = value.strip()
    #     return value

class File(TimeStampedModel):
    id = models.CharField(max_length=32, primary_key=True) # ex. 128c8661c25d45b8-9ca7809a09619db9
    name = models.CharField(max_length=255,  # display name
        validators=[RegexValidator(file_re, r'File names must not contain  \ / : * ? " < > |')])
    owner = models.ForeignKey(User, models.CASCADE, null=True, blank=True)
    parent_folder = models.ForeignKey(Folder, models.CASCADE, null=True, blank=True)
    # content points to child models
    # file = models.OneToOneField(File, models.CASCADE, parent_link=True, related_name='content')

    def __unicode__(self):
        return '{0} ({1})'.format(self.name, self.id[:6])

    class Meta(TimeStampedModel.Meta):
        pass