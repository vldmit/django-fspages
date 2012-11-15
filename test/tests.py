import sys
import unittest
import logging
from os.path import dirname, abspath, pardir, join as pjoin

here = abspath(dirname(__file__))
parent = pjoin(here, pardir)
sys.path.insert(0, parent)

from django.conf import settings
import settings as test_settings
settings.configure(test_settings)

# We can now load django-dependent modules
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase
from fspages.storage import FSPageStorage
from django.core.files.storage import FileSystemStorage

logger = logging.getLogger('fspages') # disable fspages logs as no loggers are initialized by Django
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
nullhandler = logger.addHandler(NullHandler())

class FSPageTests(TestCase):
    "Tests fspage.views.serve"
    
    def test_serve(self):
        "Test page, template rendering, metadata file parsing"
        response = self.client.get('/pages/foo.html')
        self.assertContains(response, "VALUE")
    
    def test_index(self):
        response = self.client.get('/pages/')
        self.assertContains(response, "Default locale index page")        

    def test_localized_template(self):
        response = self.client.get('/de/i18n_pages/')
        self.assertContains(response, "Deutsch lokalen")
        self.assertEqual(response['Content-Language'], 'de')
        # fallback to default language
        response = self.client.get('/de/i18n_pages/foo.html')
        self.assertContains(response, "VALUE")
        self.assertEqual(response['Content-Language'], 'en-us')
    
    def test_nonexistent_page(self):
        response = self.client.get('/pages/nonexistent')
        self.assertEqual(response.status_code, 404)
        response = self.client.get('/de/i18n_pages/nonexistent')
        self.assertEqual(response.status_code, 404)
        
    def test_documentroot_required(self):
        self.assertRaises(ImproperlyConfigured, self.client.get, '/no_document_root/page.txt')
        
    def test_path_cleaning(self):
        response = self.client.get('/pages//../../../////\\foo.html')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], "http://testserver/pages/foo.html")
    
    def test_nonvalid_metadata_file(self):
        response = self.client.get('/pages/bar.txt')
        self.assertContains(response, "Text template")
    
    def test_redirect(self):
        response = self.client.get('/pages/redirect')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], "http://somedomain/somepath")
    
    def test_forbid_metadata_extensions(self):
        response = self.client.get('/pages/foo.html.meta.json')
        self.assertEqual(response.status_code, 403)

class FSPageStorageTests(TestCase):
    """
    Test fspages.storage.FSPageStorage
    """
    storage = FSPageStorage(backend=FileSystemStorage(location=pjoin(here, 'test_pages')))
    
    def test_improper_init(self):
        self.assertRaises(ImproperlyConfigured, FSPageStorage)
    
    def test_nonmixed_storage(self):
        from django.core.files.storage import Storage
        custom = type('CustomStorage', (Storage,), {})
        self.assertRaises(ImproperlyConfigured, FSPageStorage, backend=custom())
    
    def test_mixed_storage(self):
        from fspages.storage import FileSystemStorageMixin
        custom = type('CustomStorage', (FileSystemStorage, FileSystemStorageMixin), {})
        fsp = FSPageStorage(backend=custom(location=pjoin(here, 'test_pages')))
        self.assertEqual(fsp.storage.__class__, custom)

    def test_default_language(self):
        page = self.storage.get('index.html')
        self.assertEqual(page.language, settings.LANGUAGE_CODE)
        self.assertGreater(page.data.find('Default'), -1)
    
    def test_i18n_page(self):
        page = self.storage.get('index.html', 'de')
        self.assertEqual(page.language, 'de')
        self.assertEqual(page.path, 'index.html')
        self.assertGreater(page.data.find('Deutsch'), -1)

    def test_i18n_fallback(self):
        page = self.storage.get('foo.html', 'de')
        self.assertEqual(page.language, settings.LANGUAGE_CODE)
        self.assertGreater(page.data.find('File available only in default locale'), -1)
    
    def test_i18n_no_fallback(self):
        from django.core.exceptions import ObjectDoesNotExist
        self.assertRaises(ObjectDoesNotExist, self.storage.get, 'foo.html', 'de', False)
    
    def test_only_metada_file(self):
        page = self.storage.get('baz.txt')
        self.assertEqual(len(page.data), 0)
        
        
if __name__ == '__main__':
    unittest.main()
