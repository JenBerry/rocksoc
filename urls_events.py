from datetime import date, datetime as DateTime

from django.conf.urls import *
from django.views.generic.base import RedirectView

from rocksoc.models import Event
from rocksoc.EventCalendar import ICalendarEventCalendar
from rocksoc.views import EventFutureList

def get_event_years():
    return Event.objects_in_past.dates('edatetime', 'year')

def get_photo_years():
    return Event.objects_with_photos.dates('edatetime', 'year')

urlpatterns = patterns('',
    (r'^$', EventFutureList.as_view ()),

    (r'^icalendar/$', ICalendarEventCalendar ()),
    (r'^icalendar/(?P<event_category_tag>[^/]+)/?$', ICalendarEventCalendar ()),

    (r'^(?P<year>[0-9][0-9][0-9][0-9])/?$',
      'rocksoc.views.archive_year',
     dict(date_field='edatetime', queryset=Event.objects_in_past.all(),
          template_name='events_past.html',
          allow_future=False, template_object_name='event',
          make_object_list=True,
          extra_context={'relevant_years': get_event_years,
                      })),

    (r'^photos/$', 'rocksoc.views.events_photos'),

    # for the moment just redirect from the RSS item IDs to the events page
    (r'^ljfeed/', RedirectView.as_view (url = '/events/')),

    # Backwards compatible junk
    (r'^events-future', RedirectView.as_view (url = '/events/')),
    (r'^index', RedirectView.as_view (url = '/events/')),
    (r'^(?:1999|200[0-5])/publicity/(?P<page>.*)$', RedirectView.as_view (url = '/publicity/%(page)s/')),
    (r'^(?:1999|200[0-5])/reviews/(?P<page>.*)\.txt/$', RedirectView.as_view (url = '/reviews/%(page)s/')),
    (r'^(?:1999|200[0-5])/reviews/(?P<page>.*)\.txt$', RedirectView.as_view (url = '/reviews/%(page)s/')),
    (r'^(?:1999|200[0-5])/reviews/(?P<page>.*)$', RedirectView.as_view (url = '/reviews/%(page)s/')),
)

# vim:set sw=4 sts=4 et:
