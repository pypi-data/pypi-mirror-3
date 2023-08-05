"""
Views and functions for serving static files. These are only to be used
during development, and SHOULD NOT be used in a production setting.
"""

import mimetypes
import os
import posixpath
import re
import stat
import urllib
from email.Utils import parsedate_tz, mktime_tz
from datetime import datetime

from django.http import Http404, HttpResponse, \
            HttpResponseRedirect, HttpResponseNotModified
from django.utils.http import http_date
from django.views.generic.simple import direct_to_template


class File(object):
    def __init__(self, directory, filename):
        self.directory = directory
        self.filename = filename
        self.filepath = os.path.join(directory, filename)
        if self.is_dir:
            self.filename += '/'

    def __unicode__(self):
        return self.filepath

    @property
    def is_dir(self):
        return os.path.isdir(self.filepath)

    @property
    def mtime(self):
        try:
            return datetime.fromtimestamp(os.path.getmtime(self.filepath))
        except OSError:  # pragma: no cover
            return None

    @property
    def size(self):
        try:
            return os.path.getsize(self.filepath)
        except OSError:  # pragma: no cover
            return 0


def serve(request, path, document_root=None, show_indexes=False,
            extra_context=None, template=None):
    """
    Serve static files below a given point in the directory structure.

    To use, put a URL pattern such as::

        (r'^(?P<path>.*)$',
          'django.views.static.serve',
          {'document_root' : '/path/to/my/files/'})

    in your URLconf. You must provide the ``document_root`` param. You may
    also set ``show_indexes`` to ``True`` if you'd like to serve a basic index
    of the directory.  This index view will use the template hardcoded below,
    but if you'd like to override it, you can create a template called
    ``static/directory_index.html``.
    """

    # Clean up given path to only allow serving files below document_root.
    path = posixpath.normpath(urllib.unquote(path))
    path = path.lstrip('/')
    newpath = ''
    for part in path.split('/'):
        if not part:
            # Strip empty path components.
            continue
        drive, part = os.path.splitdrive(part)
        head, part = os.path.split(part)
        if part in (os.curdir, os.pardir):
            # Strip '.' and '..' in path.
            continue
        newpath = os.path.join(newpath, part).replace('\\', '/')
    if newpath and path != newpath:
        return HttpResponseRedirect(newpath)
    fullpath = os.path.join(document_root, newpath)
    if type(fullpath) == unicode:
        fullpath = fullpath.encode('utf8')
    if os.path.isdir(fullpath):
        if show_indexes:
            return directory_index(request, newpath, fullpath, \
                        extra_context, template)
        raise Http404("Directory indexes are not allowed here.")
    if not os.path.exists(fullpath):
        raise Http404('"%s" does not exist' % fullpath)
    # Respect the If-Modified-Since header.
    statobj = os.stat(fullpath)
    mimetype, encoding = mimetypes.guess_type(fullpath)
    mimetype = mimetype or 'application/octet-stream'
    if not was_modified_since(request.META.get('HTTP_IF_MODIFIED_SINCE'),
                              statobj[stat.ST_MTIME], statobj[stat.ST_SIZE]):
        return HttpResponseNotModified(mimetype=mimetype)
    contents = open(fullpath, 'rb').read()
    response = HttpResponse(contents, mimetype=mimetype)
    response["Last-Modified"] = http_date(statobj[stat.ST_MTIME])
    response["Content-Length"] = len(contents)
    if encoding:
        response["Content-Encoding"] = encoding
    return response


def directory_index(request, path, fullpath,
                        extra_context=None, template=None):

    files = []
    for f in sorted(os.listdir(fullpath)):
        if not f.startswith('.'):
            f = File(fullpath, f)
            files.append(f)

    context = {
        'directory': path + '/',
        'file_list': files,
        'highlight': request.GET.get('highlight'),
    }
    if extra_context:
        context.update(extra_context)
    template = template or "dirbrowser/directory_index.html"
    return direct_to_template(request, template, context)


def was_modified_since(header=None, mtime=0, size=0):
    """
    Was something modified since the user last downloaded it?

    header
      This is the value of the If-Modified-Since header.  If this is None,
      I'll just return True.

    mtime
      This is the modification time of the item we're talking about.

    size
      This is the size of the item we're talking about.
    """
    try:
        if header is None:
            raise ValueError
        matches = re.match(r"^([^;]+)(; length=([0-9]+))?$", header,
                           re.IGNORECASE)
        header_date = parsedate_tz(matches.group(1))
        if header_date is None:  # pragma: no cover
            raise ValueError
        header_mtime = mktime_tz(header_date)
        header_len = matches.group(3)
        if header_len and int(header_len) != size:  # pragma: no cover
            raise ValueError
        if mtime > header_mtime:  # pragma: no cover
            raise ValueError
    except (AttributeError, ValueError, OverflowError):
        return True
    return False
