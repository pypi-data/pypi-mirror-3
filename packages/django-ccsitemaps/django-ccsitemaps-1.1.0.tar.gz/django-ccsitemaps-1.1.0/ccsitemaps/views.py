import os, tempfile, zipfile
from django.conf import settings
from django.core.servers.basehttp import FileWrapper
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext


def index(request, key=None):
    """Note: ideally this view should never get called becasue
    you should configure your webserver to serve the statically
    generated sitemaps"""
    if key is not None:
        fname = '%ssitemap%s.xml' % (
                settings.STATIC_ROOT, key)
    else:
        fname = '%ssitemap.xml' % settings.STATIC_ROOT
    try:
        wrapper = FileWrapper(file(fname))
    except IOError:
        raise Http404('%s does not exist' % fname)
    response = HttpResponse(wrapper, content_type='text/xml')
    response['Content-Length'] = os.path.getsize(fname)
    return response

