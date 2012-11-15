# -*- coding: utf-8 -*-
from django.contrib.sitemaps import Sitemap
from fspages.storage import check_mixin

class FSPagesSitemap(Sitemap):
    def __init__(self, storage):
        self.storage = check_mixin(storage)
        
        