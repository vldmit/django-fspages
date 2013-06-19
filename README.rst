==============
django-fspages
==============

Django-fspages is a small application for serving django page templates from
the filesystem or other compatible storage. It may be used as a replacement for
``django.contrib.flatpages``, have i18n support, is decoupled from Django ORM.

Application provide a ``fspages.views.serve`` view, which does mapping
between matched path string in URL and page in the storage.

Each template may be supplemented with a serialized metadata file which have a 
same name as the template plus the entension suffix. Metadata is loaded by
calling metadata loader (JSON by default).

If internationalization is enabled in django settings, the view will at first 
look for the localized version of the template by prepending the path with 
locale name directory and fallback to default language if not translation is
available.

Rationale
---------

For a django-powered website with dozens of semi-static web pages, usage of
flatpages may not always be a convenient, as several problem would arise soon:

- flatpages does not support i18n content. You can not by default provide a
  version of page both in English and Deutsch languages.

- flatpage content is a static HTML code, you can use django template language
  there, access template context, etc. You can't fill several template's
  placeholders without creating own flatpage object.

- there are two separate paths of customizing the site appearance by
  the editors - by modifying templates (served from the file system by 
  default), then editing HTML content of ``FlatPage`` object (via django admin 
  interface).

- version control of the ``FlatPage`` objects require additional integration
  with tools like django-reversion

Django-fspages tries to solve this problems by utilizing django storage api
for storing pages objects and render them as the templates. Site editors 
can edit pages as regular files with their favorite editors and version
control systems.

FAQ
---

Why not pre-render/serve static files?
  Static site generators work fine for their tasks, django-fspages is for sites
  which need to have semi-static pages (i.e. content depends on request
  parameters such as client IP address).

Why not to use template loader?
  Comparing with dumb template rendering, django-fspages support correct path
  mapping, HTML redirects, metadata processing, i18n, sitemaps.

Installation and usage
----------------------

Add ``fspages`` to settings.INSTALLED_APPS

Add ``fspages.views.serve`` into your urlconf, example:

::

  from django.core.files.storage import FileSystemStorage
  from fspages.storage import FSPageStorage
  
  fspages_storage = FSPageStorage(
    backend=FileSystemStorage(location='/path/to/pages/'))
  
  i18n_storage = FSPageStorage(
    backend=FileSystemStorage(location='/another/path/to/pages/'),
    index_document='index.html',
    metadata_extension='.meta.json')
  
  urlpatterns = patterns('',
      url(r'^pages/(?P<path>.*)$', 'fspages.views.serve', {
          'storage': fspages_storage, 
          }, 'fspages'),
  )
  
  urlpatterns += i18n_patterns('',
      url(r'^i18n_pages/(?P<path>.*)$', 'fspages.views.serve', {
          'storage': i18n_storage, 
          }, 'i18n_fspages')
  )

View options
------------

``serve`` view have two required parameters, and few optional parameters:

path (required)
  Path string matched in urlpattern, which to be mapped to page template. 

storage (required)
  fspages.storage.FSPageStorage instance

FSPageStorage constructor parameters
------------------------------------

backend (required)
  django storage object instance, usually ``FileSystemStorage``. django-fspages
  automatically extends ``FileSystemStorage`` with additional required methods
  declared in ``fspages.storage.StorageMixin``. For other storage classes, you
  would need to provide those mixins on your own.

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
