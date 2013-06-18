# -*- coding: utf-8 -*-
from .utils import find_paths

from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse
from django.utils.translation import activate

class FSPagesSitemap(Sitemap):
    def __init__(self, storage, pattern_name):
        self.storage = storage
        self.language_prefixes = storage.enabled_languages()
        self.pattern_name = pattern_name
        
    def items(self):
        items = []
        for path in find_paths('', self.storage):
            items.append(self.storage.get(path))
        for language in self.language_prefixes:
            for path in find_paths('', self.storage, language=language):
                items.append(self.storage.get(path, lang=language, fallback=False))
        return items
            
    def location(self, obj):
        activate(obj.language)
        location = reverse(self.pattern_name, kwargs={ 'path': obj.path })
        return location
    
    def lastmod(self, obj):
        return obj.lastmod()
    
    def changefreq(self, obj):
        return obj.metadata['sitemap_changefreq']

    def priority(self, obj):
        return obj.metadata['sitemap_priority']
