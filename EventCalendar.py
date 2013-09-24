from datetime import datetime as DateTime, date, timedelta
from icalendar import Calendar, Event as ICalendarEvent, vCalAddress, vDatetime
from django.db.models import get_model
from django.http import HttpResponse
from django.contrib.sites.models import Site
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist

from rocksoc.models import Event, EventCategory

"""
iCalendar event calendar for Rocksoc events. Requires icalendar to be installed.
Loosely based on: http://djangosnippets.org/snippets/2223/
Standards: http://tools.ietf.org/html/rfc5545
"""
class ICalendarEventCalendar (object):
    def __call__ (self, request, *args, **kwargs):
        try:
            obj = self.get_object (request, *args, **kwargs)
        except ObjectDoesNotExist:
            raise Http404 ('Calendar object does not exist.')
        cal = self.get_calendar (obj, request)
        response = HttpResponse (cal.to_ical (), content_type = 'text/calendar')

        site = Site.objects.get_current ()
        response['Content-Disposition'] = 'attachment; filename=%s.ics' % site.name

        return response

    """
    TODO
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
    Get the events in the calendar. obj is either None or an EventCategory whose
    items should be returned. If obj is None, all events should be returned.
    """
    def items (self, obj):
        items = Event.objects.filter (edatetime__gte = DateTime.now () - timedelta (14)) # days

        if obj is not None:
            items = items.filter (category = obj)

        return items

    def get_calendar (self, obj, request):
        cal = Calendar ()
        site = Site.objects.get_current ()

        if obj is None:
            cal.add ('prodid', '-//Rocksoc Events Calendar//%s//' % site.domain)
        else:
            cal.add ('prodid', '-//Rocksoc Events Calendar//%s//%s' % (site.domain, obj.name or ''))
        cal.add ('version', '2.0')

        # FIXME: Currently, time zones aren't taken into account at all. This
        # might cause problems for people using the calendar from different
        # time zones. This hasn't been fixed yet because none of the site is
        # time-zone-aware (since capability for it was only added in Django
        # 1.4).

        for item in self.items (obj):
            ical_event = ICalendarEvent ()

            ical_event.set ('summary', item.ename)
            if item.edescription:
                ical_event.set ('description', item.edescription)
            if item.venue:
                ical_event.add ('location', item.venue)
            # FIXME: Can't get this to work with CN
            #if item.organised_by != '':
            #    address = vCalAddress ('')
            #    address.params['cn'] = item.organised_by
            #    ical_event.add ('organizer', address)
            if item.elink:
                if item.elink.startswith ('http:') or item.elink.startswith ('https:'):
                    ical_event.add ('url', item.elink)
                else:
                    ical_event.add ('url', 'http://%s/%s' % (
                        Site.objects.get_current ().domain,
                        item.elink,
                    ))
            if item.category:
                ical_event.add ('categories', item.category.name)
            if item.eoutlink:
                ical_event.add ('attach', item.eoutlink)

            ical_event.set ('dtstart', vDatetime (item.edatetime), encode = False)
            end_time = item.get_finish_datetime () and item.get_finish_datetime () or item.edatetime
            ical_event.set ('dtend', vDatetime (end_time), encode = False)
            ical_event.set ('dtstamp', vDatetime (end_time), encode = False)
            if item.last_modified:
                ical_event.set ('last-modified', vDatetime (item.last_modified), encode = False)

            ical_event.set ('uid', '%d@%s' % (item.id, site.domain))

            cal.add_component (ical_event)

        return cal
