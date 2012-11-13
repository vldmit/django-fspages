==============
django-fspages
==============

Django-fspages is a small application for serving django page templates from
the filesystem. It may be used as a substitute for ``django.contrib.flatpages``,
have i18n support, decoupled from Django ORM

Application provide a ``fspages.views.serve`` view, which does mapping
between matched path string in URL and page in the filesystem.

Each template may be supplemented with a serialized metadata file which have a 
same name as the template plus the entension suffix. Metadata is loaded by
calling metadata loader (JSON by default).

If internationalization is enabled in django settings, the view will at first 
look for the localized version of the template by prepending the path with 
locale name directory and fallback to default language if not translation is
available.

Rationale
---------

TODO

+i18n
+revision control

Why not prerender/serve static files?
Why not to use template loader?


Installation
------------

Add ``fspages`` to settings.INSTALLED_APPS

Add ``fspages.views.serve`` into your urlconf, example:

::

  urlpatterns = patterns('',
      url(r'^pages/(?P<path>.*)$', 'fspages.views.serve', {
          'document_root': '/path/to/pages/', 
          }, 'fspages'),
  )
  
  urlpatterns += i18n_patterns('',
      url(r'^i18n_pages/(?P<path>.*)$', 'fspages.views.serve', {
          'document_root': '/another/path/to/your/i18/pages', 
          }, 'i18n_fspages')
  )

View options
------------

``serve`` view have two required parameters, and few optional parameters:

path (required)
  Path string matched in urlpattern, which to be mapped to page template. 

document_root (required)
  Path to the root directory of your pages

index_document
  When ``path`` points to the directory, view tries to open ``index_document``
  instead. Default: ``index.html``

metadata_extension
  File extension for metadata files. Default: ``.meta.json``

metadata_loader
  Callable which reveive a string with metadata file contents and needs to
  return a python dictionary. Default: json loader

metadata_defaults
  Default metadata values. Default ``fspages.views.METADATA_DEFAULTS``

Metadata parameters
-------------------

Each page may be supplied with a metadata file with additional configuration
parameters:

status_code
  HTTP status code to respond with. Default: 200

template_context
  Django template context to use in addition to ``RequestContext``.
  Default: empty dictionary.

content-type
  Custom content type. Default: mimetypes guessed type.

encoding
  Page file encoding. Default: ``utf-8``.

redirect_path
  Place an URL of a target page if you need to do HTTP redirect. Page file
  *SHOULD* be in place, it may be empty. Default: ``False``
