from __future__ import absolute_import, unicode_literals
import re
import sys
import json
from collections import OrderedDict

from django.db import models
from django.db.models.fields.files import FieldFile
from django.core.validators import RegexValidator

from rest_framework import serializers
from rest_framework import filters
from rest_framework import fields
from rest_framework import relations

from .models import Folder, File


folder_re = re.compile(r'^[^\\/:*?"<>|\.]+$', re.U)
file_re = re.compile(r'^[^\\/:*?"<>|]+$', re.U)


class ContentRelatedField(serializers.RelatedField):
    """
    A custom field to use for a file's 'content' generic relationship.
    """
    ignore_keys = set([
        "name",
        "created",
        "_state",
        "modified",
        "file_model_id",
        "content_type_id",
        "folder_id",
        "content_id",
        "type",
        "id",
        "owner_id"
    ])

    def to_representation(self, value):
        """
        Serialize tagged objects to a simple textual representation.
        """
        content = {}
        for k in value.__dict__:
            if k not in self.ignore_keys and k[-6:] != '_cache':
                v = getattr(value, k)
                if isinstance(v, FieldFile):
                    content[k] = v.url
                else:
                    content[k] = v
        return content


class FileSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(format='hex', read_only=True)
    name = serializers.CharField(max_length=255,  # display name
        validators=[RegexValidator(file_re, r'File names must not contain  \ / : * ? " < > |')])
    type = serializers.CharField(max_length=32, read_only=True, # look up in FileType model
        validators=[RegexValidator(file_re, r'File type must not contain  \ / : * ? " < > |')])
    content = ContentRelatedField(read_only=True)

    class Meta:
        model = File
        read_only_fields = ['id', 'type', 'created', 'modified', 'owner', 'content']
        fields = read_only_fields + ['name', 'folder']

    def to_representation(self, instance):
        """
        Object instance -> Dict of primitive datatypes.
        """
        # recursive check
        if type(instance).__name__ != type(instance.content).__name__:
            # get the module, will raise KeyError if module cannot be found
            # get the class, will raise AttributeError if class cannot be found
            try:
                app_label = instance.content_type.app_label
                model_class_name = type(instance.content).__name__
                serializer = getattr(sys.modules[app_label + '.serializers'], model_class_name + 'Serializer')()
                return serializer.to_representation(instance.content)
            except (KeyError, AttributeError):
                pass
        ret = OrderedDict()

        for field in self._readable_fields:
            try:
                attribute = field.get_attribute(instance)
            except fields.SkipField:
                continue

            # We skip `to_representation` for `None` values so that fields do
            # not have to explicitly deal with that case.
            #
            # For related fields with `use_pk_only_optimization` we need to
            # resolve the pk value.
            check_for_none = attribute.pk if isinstance(attribute, relations.PKOnlyObject) else attribute
            if check_for_none is None:
                ret[field.field_name] = None
            else:
                ret[field.field_name] = field.to_representation(attribute)

        return ret

class FolderFilesSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(format='hex', read_only=True)
    name = serializers.CharField(max_length=255,  # display name
        validators=[RegexValidator(file_re, r'File names must not contain  \ / : * ? " < > |')])
    type = serializers.CharField(max_length=32, read_only=True, # look up in FileType model
        validators=[RegexValidator(file_re, r'File type must not contain  \ / : * ? " < > |')])
    content = ContentRelatedField(read_only=True)

    class Meta:
        model = File
        read_only_fields = ['id', 'type', 'created', 'modified', 'owner', 'content']
        fields = read_only_fields + ['name', 'folder']

    def to_representation(self, instance):
        """
        Object instance -> Dict of primitive datatypes.
        """
        # recursive check
        if type(instance).__name__ != type(instance.content).__name__ and type(instance.content).__name__ != 'Folder':
            # get the module, will raise KeyError if module cannot be found
            # get the class, will raise AttributeError if class cannot be found
            try:
                app_label = instance.content_type.app_label
                model_class_name = type(instance.content).__name__
                serializer = getattr(sys.modules[app_label + '.serializers'], model_class_name + 'Serializer')()
                return serializer.to_representation(instance.content)
            except (KeyError, AttributeError):
                pass
        ret = OrderedDict()

        for field in self._readable_fields:
            try:
                attribute = field.get_attribute(instance)
            except fields.SkipField:
                continue

            # We skip `to_representation` for `None` values so that fields do
            # not have to explicitly deal with that case.
            #
            # For related fields with `use_pk_only_optimization` we need to
            # resolve the pk value.
            check_for_none = attribute.pk if isinstance(attribute, relations.PKOnlyObject) else attribute
            if check_for_none is None:
                ret[field.field_name] = None
            else:
                ret[field.field_name] = field.to_representation(attribute)

        return ret


class FolderSerializer(FileSerializer):
    name = serializers.CharField(max_length=255,  # display name
        validators=[RegexValidator(folder_re, r'Folder names must not contain  \ / : * ? " < > | .')])
    type = serializers.CharField(max_length=32, read_only=True)
    files = FolderFilesSerializer(many=True, read_only=True)

    class Meta:
        model = Folder
        read_only_fields = ['id', 'type', 'created', 'modified', 'files', 'owner', 'path', 'breadcrumbs']
        fields = read_only_fields + ['name', 'folder']
        # Model fields which have editable=False set, and AutoField fields will be set to read-only by default,
        # and do not need to be added to the read_only_fields option.

    # def create(self, validated_data):
    #    return CellC2Task.objects.create(**validated_data)

    # def validate_file

    # built-in
    # def __init__(self, instance=None, data=empty, **kwargs): # BaseSerializer
    #     self.instance = instance
    #     if data is not empty:
    #         self.initial_data = data
    #     self.partial = kwargs.pop('partial', False)
    #     self._context = kwargs.pop('context', {})
    #     kwargs.pop('many', None)
    #     super(BaseSerializer, self).__init__(**kwargs)

    # def is_valid(self, raise_exception=False): # BaseSerializer
    #     self._validated_data = self.run_validation(self.initial_data)

    #     return not bool(self._errors)

    # def run_validation(self, data=empty): # Serializer
    #     """
    #     We override the default `run_validation`, because the validation
    #     performed by validators and the `.validate()` method should
    #     be coerced into an error dictionary with a 'non_fields_error' key.
    #     """
    #     (is_empty_value, data) = self.validate_empty_values(data)
    #     if is_empty_value:
    #         return data

    #     value = self.to_internal_value(data)
    #     try:
    #         self.run_validators(value)
    #         value = self.validate(value)
    #         assert value is not None, '.validate() should return the validated data'
    #     except (ValidationError, DjangoValidationError) as exc:
    #         raise ValidationError(detail=get_validation_error_detail(exc))

    #     return value

    # def validate_empty_values(self, data): # Field
    #     """
    #     Validate empty values, and either:
    #     * Raise `ValidationError`, indicating invalid data.
    #     * Raise `SkipField`, indicating that the field should be ignored.
    #     * Return (True, data), indicating an empty value that should be
    #       returned without any further validation being applied.
    #     * Return (False, data), indicating a non-empty value, that should
    #       have validation applied as normal.
    #     """
    #     if self.read_only:
    #         return (True, self.get_default())

    #     if data is empty:
    #         if getattr(self.root, 'partial', False):
    #             raise SkipField()
    #         if self.required:
    #             self.fail('required')
    #         return (True, self.get_default())

    #     if data is None:
    #         if not self.allow_null:
    #             self.fail('null')
    #         return (True, None)

    #     return (False, data)

    # @property
    # def fields(self):
    #     """
    #     A dictionary of {field_name: field_instance}.
    #     """
    #     # `fields` is evaluated lazily. We do this to ensure that we don't
    #     # have issues importing modules that use ModelSerializers as fields,
    #     # even if Django's app-loading stage has not yet run.
    #     if not hasattr(self, '_fields'):
    #         self._fields = BindingDict(self)
    #         for key, value in self.get_fields().items():
    #             self._fields[key] = value
    #     return self._fields

    # @cached_property
    # def _writable_fields(self): # Serializer
    #     return [
    #         field for field in self.fields.values()
    #         if (not field.read_only) or (field.default is not empty)
    #     ]

    # def to_internal_value(self, data): # Serializer
    #     """
    #     Dict of native values <- Dict of primitive datatypes.
    #     """
    #     if not isinstance(data, dict):
    #         message = self.error_messages['invalid'].format(
    #             datatype=type(data).__name__
    #         )
    #         raise ValidationError({
    #             api_settings.NON_FIELD_ERRORS_KEY: [message]
    #         })

    #     ret = OrderedDict()
    #     errors = OrderedDict()
    #     fields = self._writable_fields # list of Field objects

    #     for field in fields:
    #         validate_method = getattr(self, 'validate_' + field.field_name, None)
    #         primitive_value = field.get_value(data) # UploadedFile object
    #         try:
    #             validated_value = field.run_validation(primitive_value) # Unmodified UploadedFile object
    #             if validate_method is not None:
    #                 validated_value = validate_method(validated_value)
    #         except ValidationError as exc:
    #             errors[field.field_name] = exc.detail
    #         except DjangoValidationError as exc:
    #             errors[field.field_name] = list(exc.messages)
    #         except SkipField:
    #             pass
    #         else:
    #             set_value(ret, field.source_attrs, validated_value)

    #     if errors:
    #         raise ValidationError(errors)

    #     return ret

    # def run_validation(self, data=empty): # Field
    #     """
    #     Validate a simple representation and return the internal value.
    #     The provided data may be `empty` if no representation was included
    #     in the input.
    #     May raise `SkipField` if the field should not be included in the
    #     validated data.
    #     """
    #     (is_empty_value, data) = self.validate_empty_values(data)
    #     if is_empty_value:
    #         return data
    #     value = self.to_internal_value(data)
    #     self.run_validators(value)
    #     return value

    # def to_internal_value(self, data): # ImageField
    #     # Image validation is a bit grungy, so we'll just outright
    #     # defer to Django's implementation so we don't need to
    #     # consider it, or treat PIL as a test dependency.
    #     file_object = super(ImageField, self).to_internal_value(data)
    #     django_field = self._DjangoImageField()
    #     django_field.error_messages = self.error_messages
    #     # returns a new file object with
    #     # f.image = image (Image.open(file))
    #     # f.content_type = Image.MIME.get(image.format)
    #     # but DRF doesn't use it
    #     django_field.to_python(file_object)
    #     return file_object

    # class ImageField(FileField): # form field
    #     default_error_messages = {
    #         'invalid_image': _(
    #             "Upload a valid image. The file you uploaded was either not an "
    #             "image or a corrupted image."
    #         ),
    #     }

    #     def to_python(self, data): # FileField
    #         if data in self.empty_values:
    #             return None

    #         # UploadedFile objects should have name and size attributes.
    #         try:
    #             file_name = data.name
    #             file_size = data.size
    #         except AttributeError:
    #             raise ValidationError(self.error_messages['invalid'], code='invalid')

    #         if self.max_length is not None and len(file_name) > self.max_length:
    #             params = {'max': self.max_length, 'length': len(file_name)}
    #             raise ValidationError(self.error_messages['max_length'], code='max_length', params=params)
    #         if not file_name:
    #             raise ValidationError(self.error_messages['invalid'], code='invalid')
    #         if not self.allow_empty_file and not file_size:
    #             raise ValidationError(self.error_messages['empty'], code='empty')

    #         return data  # UploadedFile object

    #     def to_python(self, data): # ImageField
    #         """
    #         Checks that the file-upload field data contains a valid image (GIF, JPG,
    #         PNG, possibly others -- whatever the Python Imaging Library supports).
    #         """
    #         f = super(ImageField, self).to_python(data)  # UploadedFile object
    #         if f is None:
    #             return None

    #         from PIL import Image

    #         # We need to get a file object for Pillow. We might have a path or we might
    #         # have to read the data into memory.
    #         if hasattr(data, 'temporary_file_path'):
    #             file = data.temporary_file_path()
    #         else:
    #             if hasattr(data, 'read'):
    #                 file = BytesIO(data.read())
    #             else:
    #                 file = BytesIO(data['content'])

    #         try:
    #             # load() could spot a truncated JPEG, but it loads the entire
    #             # image in memory, which is a DoS vector. See #3848 and #18520.
    #             image = Image.open(file)
    #             # verify() must be called immediately after the constructor.
    #             image.verify()

    #             # Annotating so subclasses can reuse it for their own validation
    #             f.image = image
    #             # Pillow doesn't detect the MIME type of all formats. In those
    #             # cases, content_type will be None.
    #             f.content_type = Image.MIME.get(image.format)
    #         except Exception:
    #             # Pillow doesn't recognize it as an image.
    #             six.reraise(ValidationError, ValidationError(
    #                 self.error_messages['invalid_image'],
    #                 code='invalid_image',
    #             ), sys.exc_info()[2])
    #         if hasattr(f, 'seek') and callable(f.seek):
    #             f.seek(0)
    #         return f

    # def to_internal_value(self, data): # FileField
    #     try:
    #         # `UploadedFile` objects should have name and size attributes.
    #         file_name = data.name
    #         file_size = data.size
    #     except AttributeError:
    #         self.fail('invalid')

    #     if not file_name:
    #         self.fail('no_name')
    #     if not self.allow_empty_file and not file_size:
    #         self.fail('empty')
    #     if self.max_length and len(file_name) > self.max_length:
    #         self.fail('max_length', max_length=self.max_length, length=len(file_name))

    #     return data

    # def run_validators(self, value):
    #     """
    #     Test the given value against all the validators on the field,
    #     and either raise a `ValidationError` or simply return.
    #     """
    #     errors = []
    #     for validator in self.validators: # empty
    #         if hasattr(validator, 'set_context'):
    #             validator.set_context(self)

    #         try:
    #             validator(value)
    #         except ValidationError as exc:
    #             # If the validation error contains a mapping of fields to
    #             # errors then simply raise it immediately rather than
    #             # attempting to accumulate a list of errors.
    #             if isinstance(exc.detail, dict):
    #                 raise
    #             errors.extend(exc.detail)
    #         except DjangoValidationError as exc:
    #             errors.extend(exc.messages)
    #     if errors:
    #         raise ValidationError(errors)

    # # uploaded_file = request.FILES['file']
    # # During file uploads, the actual file data is stored in request.FILES.
    # # Each entry in this dictionary is an UploadedFile object
    # def get_value(self, dictionary): # Field
    #     """
    #     Given the *incoming* primitive data, return the value for this field
    #     that should be validated and transformed to a native value.
    #     """
    #     if html.is_html_input(dictionary):
    #         # HTML forms will represent empty fields as '', and cannot
    #         # represent None or False values directly.
    #         if self.field_name not in dictionary:
    #             if getattr(self.root, 'partial', False):
    #                 return empty
    #             return self.default_empty_html
    #         ret = dictionary[self.field_name]
    #         if ret == '' and self.allow_null:
    #             # If the field is blank, and null is a valid value then
    #             # determine if we should use null instead.
    #             return '' if getattr(self, 'allow_blank', False) else None
    #         elif ret == '' and not self.required:
    #             # If the field is blank, and emptyness is valid then
    #             # determine if we should use emptyness instead.
    #             return '' if getattr(self, 'allow_blank', False) else empty
    #         return ret
    #     return dictionary.get(self.field_name, empty)

    # def save(self, **kwargs): # BaseSerializer
    #     validated_data = dict(
    #         list(self.validated_data.items()) +
    #         list(kwargs.items())
    #     )

    #     if self.instance is not None:
    #         self.instance = self.update(self.instance, validated_data)
    #     else:
    #         self.instance = self.create(validated_data)

    #     return self.instance

    # @property
    # def validated_data(self):
    #     if not hasattr(self, '_validated_data'):
    #         msg = 'You must call `.is_valid()` before accessing `.validated_data`.'
    #         raise AssertionError(msg)
    #     return self._validated_data

    # # validated_data = {
    # #     file: UploadedFile object
    # # }
    # def create(self, validated_data): # ModelSerializer
    #     """
    #     We have a bit of extra checking around this in order to provide
    #     descriptive messages when something goes wrong, but this method is
    #     essentially just:
    #         return ExampleModel.objects.create(**validated_data)
    #     If there are many to many fields present on the instance then they
    #     cannot be set until the model is instantiated, in which case the
    #     implementation is like so:
    #         example_relationship = validated_data.pop('example_relationship')
    #         instance = ExampleModel.objects.create(**validated_data)
    #         instance.example_relationship = example_relationship
    #         return instance
    #     The default implementation also does not handle nested relationships.
    #     If you want to support writable nested relationships you'll need
    #     to write an explicit `.create()` method.
    #     """
    #     raise_errors_on_nested_writes('create', self, validated_data)

    #     ModelClass = self.Meta.model

    #     # Remove many-to-many relationships from validated_data.
    #     # They are not valid arguments to the default `.create()` method,
    #     # as they require that the instance has already been saved.
    #     info = model_meta.get_field_info(ModelClass)
    #     many_to_many = {}
    #     for field_name, relation_info in info.relations.items():
    #         if relation_info.to_many and (field_name in validated_data):
    #             many_to_many[field_name] = validated_data.pop(field_name)

    #     try:
    #         instance = ModelClass.objects.create(**validated_data)
    #     except TypeError as exc:
    #         msg = (
    #             'Got a `TypeError` when calling `%s.objects.create()`. '
    #             'This may be because you have a writable field on the '
    #             'serializer class that is not a valid argument to '
    #             '`%s.objects.create()`. You may need to make the field '
    #             'read-only, or override the %s.create() method to handle '
    #             'this correctly.\nOriginal exception text was: %s.' %
    #             (
    #                 ModelClass.__name__,
    #                 ModelClass.__name__,
    #                 self.__class__.__name__,
    #                 exc
    #             )
    #         )
    #         raise TypeError(msg)

    #     # Save many-to-many relationships after the instance is created.
    #     if many_to_many:
    #         for field_name, value in many_to_many.items():
    #             setattr(instance, field_name, value)

    #     return instance
