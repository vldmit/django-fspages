# -*- coding: utf-8 -*-
# StorageMixins are borrowed from https://github.com/sehmaschine/django-filebrowser/

import os, shutil
import json

from django.core.files.move import file_move_safe
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ImproperlyConfigured

METADATA_LOADERS = {
    'json': lambda x: json.loads(x)
}

METADATA_DEFAULTS = {
    'status_code': 200,
    'template_context': {},
    'content-type': None, # will be guessed with mimetypes
    'encoding': 'utf-8',
    'redirect_path': False,
}

class FSPageStorage(object):
    """
    Storage class for FSPage objects
    """
    
    def __init__(self, storage=None, index_document='index.html',
          metadata_extension='.meta.json', metadata_loader=METADATA_LOADERS['json'],
          metadata_defaults=METADATA_DEFAULTS):
        self._storage = check_mixin(storage)
    
    def get(self, obj):
        pass

class StorageMixin(object):
    """
    Adds some useful methods to the Storage class.
    """

    def isdir(self, name):
        """
        Returns true if name exists and is a directory.
        """
        raise NotImplementedError()

    def isfile(self, name):
        """
        Returns true if name exists and is a regular file.
        """
        raise NotImplementedError()

    def move(self, old_file_name, new_file_name, allow_overwrite=False):
        """
        Moves safely a file from one location to another.

        If allow_ovewrite==False and new_file_name exists, raises an exception.
        """
        raise NotImplementedError()

    def makedirs(self, name):
        """
        Creates all missing directories specified by name. Analogue to os.mkdirs().
        """
        raise NotImplementedError()

    def rmtree(self, name):
        """
        Deletes a directory and everything it contains. Analogue to shutil.rmtree().
        """
        raise NotImplementedError()


class FileSystemStorageMixin(StorageMixin):

    def isdir(self, name):
        return os.path.isdir(self.path(name))

    def isfile(self, name):
        return os.path.isfile(self.path(name))

    def move(self, old_file_name, new_file_name, allow_overwrite=False):
        file_move_safe(self.path(old_file_name), self.path(new_file_name), allow_overwrite=True)

    def makedirs(self, name):
        os.makedirs(self.path(name))

    def rmtree(self, name):
        shutil.rmtree(self.path(name))

def check_mixin(storage):
    """
    Check the storage object for isdir method, automatically add 
    FileSystemStorageMixin to FileSystemStorage, if needed
    """
    if callable(getattr(storage, 'isdir', None)) and \
        callable(getattr(storage, 'isfile', None)):
        return storage
    if issubclass(storage.__class__, FileSystemStorage):
        storage.__class__ = type('FileSystemStorage', 
                                 (FileSystemStorage, FileSystemStorageMixin,),
                                 {})
        return storage
    raise ImproperlyConfigured("Storage object must support isfile and isdir methods")
