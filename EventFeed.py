from datetime import timedelta as TimeDelta, datetime as DateTime

from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404
from django.utils.feedgenerator import Atom1Feed, Rss201rev2Feed

from rocksoc.models import Event, EventCategory

class RssFeedWithImageGenerator (Rss201rev2Feed):
    """
    Generator for RSS feeds which have icons as provided by
    Feed.feed_extra_kwargs().
    """

    def add_root_elements (self, handler):
        super (RssFeedWithImageGenerator, self).add_root_elements (handler)

        domain = Site.objects.get_current ().domain
        link = 'http://%s' % domain

        handler.startElement ('image', {})
        handler.addQuickElement ('url', self.feed['icon'])
        handler.addQuickElement ('title', 'Cambridge Rock Society')
        handler.addQuickElement ('link', link)
        handler.endElement ('image')

class AtomFeedWithImageGenerator (Atom1Feed):
    """
    Generator for Atom feeds which have logos and icons as provided by
    Feed.feed_extra_kwargs(). Also converts the feed's description to a subtitle
    if one isn't provided.
    """

    # FIXME: Fix the charset, working around a Django 1.3.0 bug.
    # See http://code.djangoproject.com/ticket/15237#comment:8
    mime_type = 'application/atom+xml; charset=utf-8'

    def __init__ (self, title, link, description, language = None,
                  author_email = None, author_name = None, author_link = None,
                  subtitle = None, categories = None, feed_url = None,
                  feed_copyright = None, feed_guid = None, ttl = None,
                  **kwargs):
        if subtitle is None:
            subtitle = description

        super (AtomFeedWithImageGenerator, self).__init__ (
            title, link, description, language, author_email, author_name,
            author_link, subtitle, categories, feed_url, feed_copyright,
            feed_guid, ttl, **kwargs
        )

    def add_root_elements (self, handler):
        super (AtomFeedWithImageGenerator, self).add_root_elements (handler)

        handler.addQuickElement ('icon', self.feed['icon'])
        handler.addQuickElement ('logo', self.feed['logo'])

class EventFeed (Feed):
    """
    Base feed class for Rocksoc event feeds

    FIXME: Meant to be abstract, but support for abstract classes was only added
    in Python 2.6, and rocksoc.org.uk runs Python 2.5
    """

    link = '/events/'
    description = 'Upcoming rock, metal, and alternative in Cambridge in the next fortnight.'

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
            'logo' : static_url + 'img/logos/logo.jpg',
        }

    """
    Get an EventCategory for the feed based on the tag passed in the URL.
    If the URL was '/rss/club-night/': event_category_tag == 'club-night' and
    the appropriate EventCategory should be returned. If the URL was '/rss/':
    event_category_tag is None and None should be returned.
    """
    def get_object (self, request, event_category_tag = None):
        if event_category_tag is not None:
            return get_object_or_404 (EventCategory, tag = event_category_tag)
        return None

    """
    Get the feed title. obj is either None or an EventCategory.
    """
    def title (self, obj):
        if obj:
            return 'Rocksoc Events Feed (rocksoc.org.uk): %s' % (
                obj.name
            )
        return 'Rocksoc Events Feed (rocksoc.org.uk)'

    """
    Get the events in the feed. obj is either None or an EventCategory whose
    items should be returned. If obj is None, all events should be returned.
    """
    def items (self, obj):
        items = Event.objects.filter (
            edatetime__gte = DateTime.now (),
            edatetime__lte = DateTime.now () + TimeDelta (days = 14)
        )

        if obj is not None:
            items = items.filter (category = obj)

        return items

    def item_title (self, item):
        date = item.edatetime.strftime ('%H:%M %a %d %b')
        return '%s, %s, %s' % (item.ename, date, item.venue)

    def item_link (self, item):
        return item.eoutlink

    def item_guid (self, item):
        return 'http://%s/events/#%s' % (
            Site.objects.get_current ().domain,
            item.id,
        )

    def item_author_name (self, item):
        author = item.organised_by
        if not author:
            author = 'Rocksoc'
        return author

    def item_description (self, item):
        return item.edescription

    def item_pubdate (self, item):
        return item.last_modified

class RssEventFeed (EventFeed):
    feed_type = RssFeedWithImageGenerator

class AtomEventFeed (EventFeed):
    feed_type = AtomFeedWithImageGenerator
