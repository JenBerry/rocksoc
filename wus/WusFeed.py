from django.conf import settings
from django.contrib.sites.models import Site

from rocksoc.models import EventCategory
from rocksoc.EventFeed import EventFeed, RssFeedWithImageGenerator
from rocksoc.EventFeed import AtomFeedWithImageGenerator

class WusFeed (EventFeed):
    """
    Base feed class for Rocksoc WUS event feeds.
    """

    link = '/wus/'
    description = 'Upcoming Wake Up Screaming club nights in the next fortnight.'

    """
    Return a dictionary containing the URLs for a logo and an icon for the feed.

    The icon is a small square icon for the feed. Used as the RSS image
    and the Atom icon.

    The logo is a larger image for the feed, which should be roughly
    twice as wide as it is tall. Used as the Atom logo.

    They have to be absolute URLs.
    """
    def feed_extra_kwargs (self, _obj):
        domain = Site.objects.get_current ().domain
        static_url = settings.STATIC_URL
        if not static_url.startswith ('http'):
            static_url = 'http://%s%s' % (domain, static_url)

        return {
            'icon' : static_url + 'img/favicon.png',
            'logo' : static_url + 'img/logos/wus-200x100.png',
        }

    """
    Always return the WUS event category.
    """
    def get_object (self, request):
        return EventCategory.objects.get (tag = 'wus')

class RssWusFeed (WusFeed):
    feed_type = RssFeedWithImageGenerator

class AtomWusFeed (WusFeed):
    feed_type = AtomFeedWithImageGenerator
