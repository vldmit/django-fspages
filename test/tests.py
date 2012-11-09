import sys
import unittest
import logging
from os.path import dirname, abspath, pardir, join as pjoin
from django.core.exceptions import ImproperlyConfigured

here = abspath(dirname(__file__))
parent = pjoin(here, pardir)
sys.path.insert(0, parent)

from django.conf import settings
import settings as test_settings
settings.configure(test_settings)
from django.test import TestCase

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

if __name__ == '__main__':
    unittest.main()
