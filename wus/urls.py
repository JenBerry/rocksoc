from django.conf.urls import *
from django.views.generic.base import RedirectView

from rocksoc.wus.WusArtistListView import WusArtistListView
from rocksoc.wus.WusArtistDetailView import WusArtistDetailView
from rocksoc.wus.WusDateListView import WusDateListView
from rocksoc.wus.WusDateDetailView import WusDateDetailView
from rocksoc.wus.WusDjListView import WusDjListView
from rocksoc.wus.WusDjDetailView import WusDjDetailView
from rocksoc.wus.WusTrackListView import WusTrackListView
from rocksoc.wus.WusTrackDetailView import WusTrackDetailView
from rocksoc.wus.WusFeed import RssWusFeed, AtomWusFeed

urlpatterns = patterns('',
    (r'^$', 'rocksoc.wus.views.index'),
    (r'^djinfo/$','rocksoc.wus.views.djinfo'),

    (r'^track/?$', WusTrackListView.as_view ()),
    (r'^track/(?P<pk>[A-Za-z0-9-_]+)/?$', WusTrackDetailView.as_view ()),
    (r'^track/([^/]+)/?$', 'rocksoc.wus.redirect.tracksbyartist'),

    (r'^dj/?$', WusDjListView.as_view ()),
    (r'^dj/(?P<pk>[^/]+)/?$', WusDjDetailView.as_view ()),

    (r'^date/?$', WusDateListView.as_view ()),
    (r'^date/(?P<year>[0-9][0-9][0-9][0-9])-'
     r'(?P<month>[0-9][0-9])-(?P<day>[0-9][0-9])/?$',
     WusDateDetailView.as_view ()),

    (r'^artist/?$', WusArtistListView.as_view ()),
    (r'^artist/(?P<pk>[A-Za-z-_0-9]+)/?$', WusArtistDetailView.as_view ()),

    (r'^rss/$', RssWusFeed ()),
    (r'^atom/$', AtomWusFeed ()),

     # Backwards compatible URLs
    (r'^artist/([^/]+)/?$', 'rocksoc.wus.redirect.tracksbyartist'),

    # better than nothing...
    (r'^wus/wus/wus-[0-9]+/?$', RedirectView.as_view (url = '/wus/')),

    (r'^venue/venue-(?:the[ _])?(?P<object_id>[a-z-_]+)\.html/?$',
     RedirectView.as_view (url = r'/venues/%(object_id)s/')),

    (r'^index', RedirectView.as_view (url = '/wus/')),

    (r'^allevents', RedirectView.as_view (url = '/wus/date/')),

    (r'^(?P<x>djinfo|generalinfo)/index',
     RedirectView.as_view (url = r'/wus/%(x)s/')),

    (r'^djs/?(?:index)?$', RedirectView.as_view (url = '/wus/dj/')),

    (r'^dj/dj[-/](?P<x>[a-zA-Z0-9]+)(?:\.html)?$',
     RedirectView.as_view (url = r'/wus/dj/%(x)s/')),

#    (r'^venue/(?![Tt]he)(?P<object_id>[a-z-_]+)/?$',
#     RedirectView.as_view (url = r'/venues/%(object_id)s/')),

    (r'^tracksbyartist/([^/]+)$', 'rocksoc.wus.redirect.tracksbyartist'),
)

# vim:set sw=4 sts=4 et:
