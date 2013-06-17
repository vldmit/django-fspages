import posixpath
import urllib
import logging

from django.http import HttpResponse, Http404, HttpResponseRedirect,\
    HttpResponseForbidden
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist,\
    SuspiciousOperation
from django.utils.translation import ugettext as _
from django.core.urlresolvers import resolve, reverse
from django.template import Template, RequestContext

logger = logging.getLogger(__name__)

def serve(request, path=None, storage=None):
    """
    Serve pages from a storage as django templates.
    
    Each template may be supplemented with a serialized metadata file which have a same
    name as the template plus metadata entension suffix.
    
    If internationalization is enabled in django settings, the view will at first look for the
    localized version of the template by prepending the path with locale name directory.
    """
    if storage is None:
        raise ImproperlyConfigured(_(u"No storage is not provided"))
    
    path = urllib.unquote(path)
    newpath = posixpath.normpath('/' + path.replace('\\', '/').lstrip('/'))
    # manually add trailing slash (see http://bugs.python.org/issue1707768 )
    if len(path) > 0 and path[-1] == '/':
        newpath += '/'
    newpath = newpath.lstrip('/')
    if path != newpath:
        resolver_match = resolve(request.path_info)
        viewname = resolver_match.url_name
        return HttpResponseRedirect(reverse(viewname, kwargs = { 'path': newpath }))
    newpath = posixpath.join(*newpath.split('/'))

    try:
        page = storage.get(newpath)
    except ObjectDoesNotExist:
        raise Http404(_(u'"%(path)s" does not exist') % {'path': path})
    except SuspiciousOperation:
        return HttpResponseForbidden(_(u'"%(path)s" is not allowed') % {'path': path})
        
    if page.metadata['redirect_path'] is not False:
        return HttpResponseRedirect(page.metadata['redirect_path'])
    
    data = page.data
    template = Template(data)
    context = RequestContext(request, page.metadata['template_context'])
    s = template.render(context)
    response = HttpResponse(s, mimetype=page.metadata['content-type'], 
                            status=page.metadata['status_code'])
    response['Content-Language'] = page.language
    return response
