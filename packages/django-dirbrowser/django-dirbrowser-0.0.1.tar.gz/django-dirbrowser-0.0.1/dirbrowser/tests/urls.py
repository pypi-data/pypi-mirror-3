"""
 Testing urls for dirbrowser

"""
import os
from django.conf.urls.defaults import patterns, url
from dirbrowser.views import serve

BROWSE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))

extra = {
    'extra_value': "value",
    'extra_context': {'extra_context': 'some text'},
}

urlpatterns = patterns('',
    url(r'^browse/(?P<path>.*)$', serve, {
        'document_root': BROWSE_DIR,
        'show_indexes': True,
        'extra_context': extra,
    }),
    url(r'^browse2/(?P<path>.*)$', serve, {
        'document_root': BROWSE_DIR,
        'show_indexes': True,
    }),
    url(r'^download/(?P<path>.*)$', serve, {
        'document_root': BROWSE_DIR,
        'show_indexes': False,
    }),
)
