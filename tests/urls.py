import os
from django.conf.urls import url, patterns
from django.conf.urls.i18n import i18n_patterns
from django.core.files.storage import FileSystemStorage
from fspages.storage import FSPageStorage

testdir = os.path.dirname(__file__) + '/test_pages/'
fsstorage = FileSystemStorage(location=testdir)
teststorage = FSPageStorage(backend=fsstorage)

urlpatterns = patterns('',
    url(r'^pages/(?P<path>.*)$', 'fspages.views.serve', {
        'storage': teststorage, 
        }, 'fspages'),
    url(r'^no_document_root/(?P<path>.*)$', 'fspages.views.serve'),
)

urlpatterns += i18n_patterns('',
    url(r'^i18n_pages/(?P<path>.*)$', 'fspages.views.serve', {
        'storage': teststorage, 
        }, 'i18n_fspages')
)
