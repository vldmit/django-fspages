import posixpath
import mimetypes
import json
import urllib
import logging

from django.http import HttpResponse, Http404, HttpResponseRedirect,\
    HttpResponseForbidden
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext as _, get_language
from django.core.urlresolvers import resolve, reverse
from django.template import Template, RequestContext
from django.conf import settings

from storage import check_mixin

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
}

def serve(request, path=None, storage=None, index_document='index.html',
          metadata_extension='.meta.json', metadata_loader=METADATA_LOADERS['json'],
          metadata_defaults=METADATA_DEFAULTS):
    """
    Serve pages from a storage as django templates.
    
    Each template may be supplemented with a serialized metadata file which have a same
    name as the template plus metadata_entension suffix. Metadata is loaded by calling
    metadata_loader, you can customize default values by providing own metadata_defaults
    
    If internationalization is enabled in django settings, the view will at first look for the
    localized version of the template by prepending the path with locale name directory.
    """
    if storage is None:
        raise ImproperlyConfigured(_(u"No storage is not provided"))
    storage = check_mixin(storage)
    
    path = urllib.unquote(path)
    newpath = posixpath.normpath('/' + path.replace('\\', '/').lstrip('/'))
    newpath = newpath.lstrip('/')
    if path != newpath:
        resolver_match = resolve(request.path_info)
        viewname = resolver_match.url_name
        return HttpResponseRedirect(reverse(viewname, kwargs = { 'path': newpath }))
    if newpath.find(metadata_extension, len(newpath) - len(metadata_extension)) > 0:
        return HttpResponseForbidden()
    
    newpath = posixpath.join(*newpath.split('/'))
    
    localepath = u"%s/%s" % ( get_language(), newpath)
    
    if storage.exists(localepath):
        newpath = localepath
        localized = True
    else:
        localized = False
    if storage.isdir(newpath):
        newpath = posixpath.join(newpath, index_document)

    metadata = metadata_defaults.copy()
    metadata_filename = newpath + metadata_extension
    if storage.isfile(metadata_filename):
        try:
            f = storage.open(metadata_filename)
            metadata.update(metadata_loader(f.read().decode('utf-8')))
        except:
            logger.error(u"Can not load metadata file: %s" % metadata_filename)
    
    if metadata['redirect_path'] is not False:
        return HttpResponseRedirect(metadata['redirect_path'])
    
    if storage.exists(newpath):
        f = storage.open(newpath)
        data = f.read().decode(metadata['encoding'])
        template = Template(data)
        context = RequestContext(request, metadata['template_context'])
        s = template.render(context)
        metadata['content-type'] = metadata['content-type'] or \
            mimetypes.guess_type(newpath)[0] or 'application/octet-stream'
        response = HttpResponse(s, mimetype=metadata['content-type'], status=metadata['status_code'])
    else:
        raise Http404(_(u'"%(path)s" does not exist') % {'path': path})
    
    if localized:
        response['Content-Language'] = get_language()
    else:
        response['Content-Language'] = settings.LANGUAGE_CODE
    
    return response
