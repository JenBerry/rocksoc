from datetime import datetime as DateTime

from django.contrib.flatpages.models import FlatPage
from django.shortcuts import render_to_response
from django.template import RequestContext

from rocksoc.models import WUSSetlistItem, Event

def index(request):
    wus_blurb = FlatPage.objects.filter(url__exact='/_bits/wus-blurb/')
    past = Event.wuses_in_past.all().order_by('-edatetime')
    future = Event.wuses_in_future.all().order_by('edatetime')
    return render_to_response ('wus/index.html', {
        'future_wus_list' : future,
        'past_wus_list' : past,
        'wus_blurb_list' : wus_blurb,
        'WUSSetlistItem' : WUSSetlistItem,
    }, context_instance = RequestContext (request))

def djinfo(request):
    djinfo_pages = FlatPage.objects.filter(url__startswith='/wus/djinfo/').order_by('url')
    return render_to_response ('wus/djinfo.html', {
        'djinfo_pages' : djinfo_pages,
    }, context_instance = RequestContext (request))

# vim:set sw=4 sts=4 et:
