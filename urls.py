from django.conf.urls import *
from django.conf import settings
from django.db import connection
from django.views.generic.base import RedirectView

from rocksoc.models import Quote, Venue, Minutes, MinutesCategory, MemberPhoto
from rocksoc.models import WUSDjSitemap, WUSSetSitemap, ArtistSitemap, TrackNameSitemap
from rocksoc.models import MemberPhotoSitemap, CommitteeSitemap, EventSitemap, MinutesSitemap
from rocksoc import admin
from rocksoc.EventFeed import RssEventFeed, AtomEventFeed
from rocksoc.StaticSitemap import StaticSitemap
from rocksoc.views import MemberPhotoList, MemberPhotoDetail, QuoteList, MinutesList, MinutesByCategoryList, MinutesDetail, VenueDetail

sitemaps = {
    'main': StaticSitemap,
    'wus-djs': WUSDjSitemap,
    'wus-sets': WUSSetSitemap,
    'artists': ArtistSitemap,
    'tracks': TrackNameSitemap,
    'members': MemberPhotoSitemap,
    'committee': CommitteeSitemap,
    'events': EventSitemap,
    'minutes': MinutesSitemap,
}

urlpatterns = patterns('',

        
    (r'^committee/(?P<committee_year>\d\d\d\d)/$', 'rocksoc.views.committee'),
    (r'^committee/current/$', 'rocksoc.views.committee_current'),
    (r'^committee/$', RedirectView.as_view (url = '/committee/current/')),
    (r'^updates/$', 'rocksoc.views.updates'),
    (r'^information/$','rocksoc.views.information'),
    (r'^promo/$', 'rocksoc.views.promo'),
    (r'^news/$', 'rocksoc.views.news'),
    (r'^flatpages/list/$','rocksoc.views.flatpages_list'),
            
    (r'^member/$','rocksoc.views.member'),     
    (r'^/?$', 'rocksoc.views.index'),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),

    (r'^feedback/?$', 'rocksoc.views.contact'),
    (r'^mailing-list/subscribe/?$', 'rocksoc.views.subscribe'),

    (r'^rss/$', RssEventFeed ()),
    (r'^rss/(?P<event_category_tag>[^/]+)/?$', RssEventFeed ()),
    (r'^atom/$', AtomEventFeed ()),
    (r'^atom/(?P<event_category_tag>[^/]+)/?$', AtomEventFeed ()),

    (r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),

    (r'^gallery/members/?$', MemberPhotoList.as_view ()),
    (r'^gallery/members/(?P<pk>[^/]+)/?$', MemberPhotoDetail.as_view ()),

    (r'^quotes/?$', QuoteList.as_view ()),

    # For simplicity, minutes' ID is actually unique across categories
    (r'^minutes/[^/]+/(?P<pk>[^/]+)/?$', MinutesDetail.as_view ()),
    (r'^minutes/(?P<category>[^/]+)/?$', MinutesByCategoryList.as_view ()),
    (r'^minutes/?$', MinutesList.as_view ()),

    (r'^venues/(?P<pk>[a-z-_]+)/?$', VenueDetail.as_view ()),

    # Other modules
    (r'^wus(?:\.html|/|$)', include('rocksoc.wus.urls')),
    (r'^events(?:/|$)', include('rocksoc.urls_events')),

    (r'^leeroy/', include(admin.site.urls)),

    # Check whether there's a backwards compatible redirect.
    # (Failing that, get the content from the flat pages table, if possible)

    # Backwards compatible junk
    (r'^RSS/', RedirectView.as_view (url = '/rss/')),
    (r'^rss\.php', RedirectView.as_view (url = '/rss/')),
    (r'^feeds/*', RedirectView.as_view (url = '/rss/')),

    (r'^index[/.]?$', RedirectView.as_view (url = '/')),
    (r'^regevents\.htm$', RedirectView.as_view (url = '/wus/')),
    (r'^(?P<page>information|constitution|history|committee|events|introduction|minutes|feedback|quotes|links|gallery)/index\.html$',
            RedirectView.as_view (url = '/%(page)s/')),
    (r'^(?P<page>information|constitution|history|committee|events|introduction|minutes|feedback|quotes|links|gallery)\.php$',
            RedirectView.as_view (url = '/%(page)s/')),
    (r'^minutes-view/minutes-view-minutes-(?P<cat>general|financial|1998-1999|1999-2000|200[0-5]-200[1-6])-(?P<page>.*)\.html$',
            RedirectView.as_view (url = '/minutes/%(cat)s/%(page)s/')),
    (r'^members/(?:members-)(?P<number>[1-9][0-9]*)(?:\.html)$',
            RedirectView.as_view (url = '/gallery/members/%(number)s/')),
    (r'^events-view-http:--www\.livejournal\.com-community-rocksoc-101557\.html\.html$',
            RedirectView.as_view (url = 'http://community.livejournal.com/rocksoc/101557.html')),
    (r'^livejournal', RedirectView.as_view (url = 'http://community.livejournal.com/rocksoc/')),
    (r'^venue/venue-kambar\.html$', RedirectView.as_view (url = '/venues/kambar/')),
    (r'^events-past-(?P<year>1999|200[0-5])', RedirectView.as_view (url = '/events/%(year)s/')),
    (r'^events-past\.', RedirectView.as_view (url = '/events/2005/')),
    (r'^events-view-events-(?P<event>.*).html$', RedirectView.as_view (url = '/events-view/%(event)s/')),
    (r'^events-view/events/(?P<event>.*)\.txt$', RedirectView.as_view (url = '/events-view/%(event)s/')),
    (r'^publicity/2007/extremenoiseterror/$', RedirectView.as_view (url = '/publicity/2007/amputated/')),
    (r'^reviews/(?P<event>.*).txt$', RedirectView.as_view (url = '/reviews/%(event)s/')),
    (r'^history', RedirectView.as_view (url = '/committee/current/')),


# redirects to amusing images for those who steal ours
    (r'^images/*',
            RedirectView.as_view (url = 'http://images4.wikia.nocookie.net/__cb20070318192247/uncyclopedia/images/3/34/Mario.gif')),

#flatpages
    (r'^(?P<url>.*)$','rocksoc.flatpages.views.flatpage'),
    #(r'^flatpage(?P<url>*)$', 'rocksoc.flatpages.views.flatpage'),
)



# vim:set sw=4 sts=4 et:
