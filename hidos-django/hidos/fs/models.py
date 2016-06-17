from __future__ import absolute_import, unicode_literals
import re
import uuid
from os import path

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

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


class FileType(models.Model):
    """app, icon, props?
    """
    pass


class File(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False) # ex. 128c8661c25d45b8-9ca7809a09619db9
    name = models.CharField(max_length=255)  # display name
        #validators=[RegexValidator(file_re, r'File names must not contain  \ / : * ? " < > |')])
    type = models.CharField(max_length=32, null=True, blank=True) # look up in FileType model
        #validators=[RegexValidator(file_re, r'File type must not contain  \ / : * ? " < > |')])
    owner = models.ForeignKey(User, models.CASCADE, null=True, blank=True)
    folder = models.ForeignKey('Folder', models.CASCADE, null=True, blank=True, related_name='files')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    content_id = models.CharField(max_length=32, null=True, blank=True)
    content = GenericForeignKey('content_type', 'content_id')

    def __unicode__(self):
        return '{0} ({1})'.format(self.name, self.id.hex[:6])

    class Meta(TimeStampedModel.Meta):
        pass


class Folder(File):
    #name = models.CharField(max_length=255)  # display name
        #validators=[RegexValidator(folder_re, r'Folder names must not contain  \ / : * ? " < > | .')])
    file_model = models.OneToOneField(File, models.CASCADE, 
        parent_link=True, related_name='+') # explicit parent link with no related name

    @property
    def path(self): # will probably need some caching
        if not self.parent_folder:
            return self.name
        else:
            return self.parent_folder.path() + '/' + self.name

    class Meta(File.Meta):
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