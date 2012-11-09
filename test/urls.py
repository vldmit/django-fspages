import os
from django.conf.urls import url, patterns
from django.conf.urls.i18n import i18n_patterns

testdir = os.path.dirname(__file__) + '/test_pages/'

urlpatterns = patterns('',
    url(r'^pages/(?P<path>.*)$', 'fspages.views.serve', {
        'document_root': testdir, 
        }, 'fspages'),
    url(r'^no_document_root/(?P<path>.*)$', 'fspages.views.serve'),
)

urlpatterns += i18n_patterns('',
    url(r'^i18n_pages/(?P<path>.*)$', 'fspages.views.serve', {
        'document_root': testdir, 
        }, 'i18n_fspages')
)
