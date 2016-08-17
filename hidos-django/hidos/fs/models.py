from __future__ import absolute_import, unicode_literals
import re
import sys
import uuid
from os import path

from django.db import models
from django.conf import settings
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


class FileManager(models.Manager):

    def create(self, name, owner, folder, **kwargs): # QuerySet
        """
        Create a new folder given the name and parent folder
        and returns the file_model
        """
        # Build data dictionary
        data = {
            'name': name,
            'folder': folder,
        }
        if not owner.is_anonymous:
            data['owner'] = owner
        #print(data)
        f = getattr(sys.modules['fs.models'], 'Folder').objects.create(**data)
        f.content = f
        f.save()
        return f.file_model


class File(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False) # ex. 128c8661c25d45b8-9ca7809a09619db9
    name = models.CharField(max_length=255)  # display name
        #validators=[RegexValidator(file_re, r'File names must not contain  \ / : * ? " < > |')])
    type = models.CharField(max_length=32, null=True, blank=True) # look up in FileType model
        #validators=[RegexValidator(file_re, r'File type must not contain  \ / : * ? " < > |')])
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE, null=True, blank=True)
    folder = models.ForeignKey('Folder', models.CASCADE, null=True, blank=True, related_name='files')
    content_type = models.ForeignKey(ContentType, models.CASCADE, null=True, blank=True)
    content_id = models.UUIDField(max_length=32, null=True, blank=True)
    content = GenericForeignKey('content_type', 'content_id')

    objects = FileManager()

    def __unicode__(self):
        return '{0} ({1})'.format(self.name, self.id.hex[:6])

    class Meta(TimeStampedModel.Meta):
        pass


class FolderManager(models.Manager):

    def create(self, name, owner, folder, **kwargs): # QuerySet
        """
        Create a new folder given the name and parent folder
        """
        # Build data dictionary
        data = {
            'name': name,
            'type': 'folder',
            'folder': folder,
        }
        if not owner.is_anonymous:
            data['owner'] = owner
        #print(data)
        obj = super(FolderManager, self).create(**data)
        obj.content = obj
        obj.save()
        return obj


class Folder(File):
    #name = models.CharField(max_length=255)  # display name
        #validators=[RegexValidator(folder_re, r'Folder names must not contain  \ / : * ? " < > | .')])
    file_model = models.OneToOneField(File, models.CASCADE,
        parent_link=True, related_name='+') # explicit parent link with no related name

    objects = FolderManager()

    home_name = 'Home'

    @property
    def path(self): # will probably need some caching
        if not self.folder:
            return self.home_name + '/' + self.name
        else:
            return self.folder.path + '/' + self.name

    def breadcrumbs(self, folder_list=None):
        """returns folder_list, with the first item being the parent folder,
        the second item being the grandparent folder, and so on.
        """
        if not folder_list:
            folder_list = []
        if not self.folder:
            return [[self.home_name, self.home_name]] + folder_list
        else:
            folder_list.append([self.folder.id.hex, self.folder.name])
            return self.folder.breadcrumbs(folder_list)

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
