from datetime import datetime as DateTime

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

from rocksoc.models import WUS, WUSSetlistItem

def index_view(request):
    future = WUS.objects.filter(date_occurs__gte=DateTime.now()).order_by('date_occurs')
    past = WUS.objects.filter(date_occurs__lt=DateTime.now()).order_by('-date_occurs')
    return render_to_response ('wus/index.html', {
        'future_wus_list' : future,
        'past_wus_list' : past,
        'WUSSetlistItem' : WUSSetlistItem,
    }, context_instance = RequestContext (request))

# vim:set sw=4 sts=4 et:
