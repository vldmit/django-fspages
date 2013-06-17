# -*- coding: utf-8 -*-
# StorageMixins are borrowed from https://github.com/sehmaschine/django-filebrowser/

import os, shutil
import json
import logging
import posixpath

from django.core.files.move import file_move_safe
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ImproperlyConfigured, SuspiciousOperation,\
    ObjectDoesNotExist
from django.utils.translation import get_language
from django.conf import settings
import mimetypes

logger = logging.getLogger(__name__)

METADATA_LOADERS = {
    'json': lambda x: json.loads(x)
}

METADATA_DEFAULTS = {
    'status_code': 200,
    'template_context': {},
    'content-type': None, # will be guessed with mimetypes
    'encoding': 'utf-8',
    'redirect_path': False,
    'sitemap_priority': 0.5,
    'sitemap_changefreq': None,
}

class FSPage(object):
    """
    Represent single page
    """
    
    def __init__(self, path, data, metadata, language, storage=None,
                 is_index=False):
        self.path = path
        self.data = data
        self.metadata = metadata
        self.storage = storage
        self.language = language
        if is_index:
            self.metadata['content-type'] = self.metadata.get('content-type') \
                or mimetypes.guess_type(self.storage.index_document)[0] or \
                'application/octet-stream'
        else:
            self.metadata['content-type'] = self.metadata.get('content-type') or \
                mimetypes.guess_type(self.path)[0] or 'application/octet-stream'
    
    def lastmod(self):
        return self.storage.lastmod(self.path)
    
    def __unicode__(self):
        return u"<Page '%s' (%s)>" % (self.path, self.language)
    
class FSPageStorage(object):
    """
    Storage class for FSPage objects
    """
    
    def __init__(self, backend=None, index_document='index.html',
          metadata_extension='.meta.json', metadata_loader=METADATA_LOADERS['json'],
          metadata_defaults=METADATA_DEFAULTS):
        if backend is None:
            raise ImproperlyConfigured(u"No django storage is not provided")        
        self.storage = check_mixin(backend)
        self.index_document = index_document
        self.metadata_extension = metadata_extension
        self.metadata_loader = metadata_loader
        self.metadata_defaults = metadata_defaults
    
    def get(self, path, lang=None, fallback=True):
        """
        Return FSPage object at the given path. A localized version of a page
        is returned.
        
        To request a page with specific language, pass language code to lang;
        fallback parameter regulates whether to return default language page or
        not if localized version is not available.
        """
        if path.find(self.metadata_extension, 
                     len(path) - len(self.metadata_extension)) > 0:
            raise SuspiciousOperation("Acccess for metadata files is not allowed")
 
        if lang is None:
            lang = get_language()
        data = metadata = None
        if lang != settings.LANGUAGE_CODE:
            localepath = u"%s/%s" % (lang, path)
            res = self._get(localepath)
            if res:
                data, metadata, is_index = res
                return FSPage(path, data, metadata, lang, storage=self,
                              is_index=is_index)
        if fallback:
            res = self._get(path)
            if res:
                data, metadata, is_index = res
                return FSPage(path, data, metadata, settings.LANGUAGE_CODE, 
                              storage=self, is_index=is_index)

        raise ObjectDoesNotExist(u"Page %s is not found" % path)
    
    def _get(self, path):
        """
        Return page string, metadata dictionary at the given path, or
        None if object is not available.
        """
        is_index = False
        if self.storage.isdir(path):
            is_index = True
            path = posixpath.join(path, self.index_document)
        
        metadata = self.metadata_defaults.copy()
        metadata_path = path + self.metadata_extension
        metadata_available = False
        if self.storage.isfile(metadata_path):
            try:
                f = self.storage.open(metadata_path)
                metadata.update(self.metadata_loader(f.read().decode('utf-8')))
                metadata_available = True
            except:
                logger.error(u"Can not load metadata file: %s" % metadata_path)
        
        if self.storage.isfile(path):
            f = self.storage.open(path)
            data = f.read().decode(metadata['encoding'])
        else:
            if metadata_available:
                logger.warning(u"Page file %s is missing while metadata is available" % path)
                data = ""
            else:
                return None
        
        return data, metadata, is_index
    
    def lastmod(self, path):
        "Return last modification time for path as datetime.datetime object"
        return self.storage.modified_time(path)
    
    def enabled_languages(self):
        "Return list of directories with translations"
        language_prefixes = map(lambda x: x[0], settings.LANGUAGES)
        language_prefixes = filter(lambda x: self.storage.isdir(x),
                                   language_prefixes)
        return language_prefixes
    
    def listdir(self, path):
        """
        Lists the contents of the specified path, returning a 2-tuple of lists;
        the first item being directories, the second item being files. For root
        path, enabled_languages() directories are filtered out. Files with 
        metadata_extensions are filtered out too.
        """

        dirs, files = self.storage.listdir(path)
        if path == "":
            enabled_languages = self.enabled_languages()
            dirs = filter(lambda x: x not in enabled_languages, dirs)
        
        files = filter(lambda x: x.find(self.metadata_extension,
                                        len(x) - len(self.metadata_extension)) == -1, files)
        
        return dirs, files

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
