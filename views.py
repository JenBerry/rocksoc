import sys
from datetime import timedelta as TimeDelta, datetime as DateTime
from datetime import date

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.views.generic import ListView, DetailView
from django.http import Http404
from django import forms
from django.template import loader, RequestContext

from rocksoc.flatpages.models import FlatPage
from rocksoc.models import Event, Minutes, Committee, MemberPhoto, Quote, Venue
from rocksoc.mail import BadHeaderError, send_mail, mail_admins

from urllib import urlopen
from smtplib import SMTPException

def index(request):
    past = Event.wuses_in_past.all()
    future = Event.wuses_in_future.all()
    _min = DateTime.now() - TimeDelta(days=1)
    _max = DateTime.now() + TimeDelta(days=14)
    selection = Event.objects.filter(edatetime__gte=_min,
                                     edatetime__lte=_max,
                                     ).order_by('edatetime')
    upcoming = FlatPage.objects.filter(url__startswith='/news/').order_by('url')
    intro = FlatPage.objects.filter(url__exact='/_bits/intro/')

    return render_to_response ('index.html', {
        'future_wus_list' : future,
        'past_wus_list' : past,
        'event_list' : selection,
        'upcoming_list' : upcoming[:1],
        'intro_list' : intro[:1],
    }, context_instance = RequestContext (request))

def get_current_committee ():
    current_year = DateTime.now ().year
    committee = Committee.objects.filter (year_elected = current_year).order_by ('order')
    if committee:
        return committee
    return Committee.objects.filter (year_elected = current_year - 1).order_by ('order')

def get_committee_years ():
    return uniqs (Committee.objects.values ('year_elected').order_by ('-year_elected'))

def uniqs(inp, was_there=[]):
    L=inp
    for object in L:
        if not object in was_there:
            was_there.append(object)
    return was_there

def committee(request, committee_year):
    committee_year = int(committee_year) # change committee_year from a string to an integer
    date = DateTime.now ().year # the current date
    committee_for_year = Committee.objects.filter(year_elected = committee_year).order_by('order') # list of committee members active in committee_year
    c = committee_for_year.count() # number of committee members in committee_year
    if (committee_year < 2002):
        error = ("too old, try looking in 'older committees'") # information on committees older than 2002 are on a flatpage
    else:
        if c == 0: # if no committee members are found for a given year it could be that it is in the future or the information has been lost
            if (committee_year < date - 1): # use date-1 because committee is elected half way through year, must be converted to string because committee_year is a string
                error = ("Member information has been lost")
            else:
                error = ("The committee for %s has not been elected yet"% committee_year)
        else:
            error = ""
    return render_to_response ('committee.html', {
        'committee_year' : committee_year,
        'committee_members' : committee_for_year,
        'number_of_committee_members' : c,
        'todays_date' : date,
        'error' : error,
        'years' : get_committee_years (),
    }, context_instance = RequestContext (request))


def committee_current(request): #mostly the same as above, but finding the current committee
    current_committee = get_current_committee ()
    c = current_committee.count()
    return render_to_response ('committee.html', {
        'committee_year' : current_committee[0].year_elected,
        'committee_members' : current_committee,
        'number_of_committee_members' : c,
        'todays_date' : DateTime.now ().year,
        'years' : get_committee_years (),
    }, context_instance = RequestContext (request))

def information(request):
    return render_to_response ('information.html', {
        'committee_members' : get_current_committee (),
        #'relevent_years' : relevent_years,
        'years' : get_committee_years (),
    }, context_instance = RequestContext (request))

class contactform(forms.Form):
    CHOICES = [('%s' % Committee.email,
               '%s <%s@>' % (Committee.position, Committee.email))
              for Committee in get_current_committee ()]
    CHOICES.insert(0, ['committee','Committee <committee@>'])
    # Set the default to the events officer, since they're most likely to be contacted
    to = forms.ChoiceField(choices=CHOICES, initial='events')
    your_name = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'size':'50'}))
    your_email = forms.EmailField(widget=forms.TextInput(attrs={'size':'50'}))
    subject = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'size':'50'}))
    message = forms.CharField(widget=forms.Textarea)

def contact(request):
    emailing = False
    crashes=[]
    if request.method == 'POST':
        emailing = True
        form = contactform(request.POST)
        if form.is_valid():
            to = form.cleaned_data['to']
            your_name = form.cleaned_data['your_name']
            your_email = form.cleaned_data['your_email']
            subject = form.cleaned_data['subject']
            message = ("Received by the Rocksoc contact form at "
                       "<http://www.rocksoc.org.uk/feedback/>.\n\n"
                       "Apparently from: %s <%s>\n"
                       "To: %s\n"
                       "Subject: %s\n\n"
                       "%s" % (your_name, your_email,
                               to, subject,
                               form.cleaned_data['message']))
            
            try:
                send_mail(subject='[Rocksoc contact form] %s' % subject,
                          message=message,
                          from_email=your_email,
                          recipient_list=[to + '@rocksoc.org.uk'],
                          fail_silently=False)
            except BadHeaderError:
                mail_admins(subject='BadHeaderError in Rocksoc contact form!',
                            message=("Failed to send a message because:\n\n"
                                     "\t%s\n\n"
                                     "The message was:\n\n%s" % (e, message)),
                            fail_silently=True)
                crashes.append("An email header contained an invalid value. "
                               "(If you're trying to break our website: please "
                               "don't do that.)")
            except SMTPException, e:
                mail_admins(subject='Failure in Rocksoc contact form!',
                            message=("Failed to send a message because:\n\n"
                                     "\t%s\n\n"
                                     "The message was:\n\n%s" % (e, message)),
                            fail_silently=True)
                crashes.append("Unable to send your email at the moment. "
                               "Sorry! Please try contacting "
                               "<tt>postmaster at rocksoc dot org dot uk</tt>")
            else:
            
                return HttpResponseRedirect('/feedback/message-sent/')

    else:
        form = contactform()
    return render_to_response ('contact_form.html', {
        'form' : form,
        'emailing' : emailing,
        'current_committee' : get_current_committee (),
    }, context_instance = RequestContext (request))

#######################################################################


def member (request):
    return render_to_response ('member.html',
                               context_instance = RequestContext (request))

def events_photos(request):
    event_list=Event.objects.all().order_by('-edatetime')
    return render_to_response ('events_photos.html', {
        'event_list' : event_list,
        'current_year' : DateTime.now ().year,
    }, context_instance = RequestContext (request))

def promo (request):
    promo_pages = FlatPage.objects.filter(url__startswith='/promo/')
    return render_to_response ('promo.html', {
        'promo_pages' : promo_pages,
    }, context_instance = RequestContext (request))


"""
archive_year is used for the events pages
copied from django.views.generic.date_based.archive_year
and modified to send past events from the current year to a different
template
"""

def archive_year(request, year, queryset, date_field, template_name=None,
        template_loader=loader, extra_context=None, allow_empty=False,
        context_processors=None, template_object_name='object', mimetype=None,
        make_object_list=False, allow_future=False):
    """
    Generic yearly archive view.

    Templates: ``<app_label>/<model_name>_archive_year.html``
    Context:
        date_list
            List of months in this year with objects
        year
            This year
        object_list
            List of objects published in the given month
            (Only available if make_object_list argument is True)
    """
    if extra_context is None: extra_context = {}
    model = queryset.model
    now = DateTime.now()

    if int(year) == now.year:
        this_year=True
    else:
        this_year=False

    lookup_kwargs = {'%s__year' % date_field: year}

    # Only bother to check current date if the year isn't in the past and future objects aren't requested.
    if int(year) >= now.year and not allow_future:
        lookup_kwargs['%s__lte' % date_field] = now
    date_list = queryset.filter(**lookup_kwargs).dates(date_field, 'month')
    if not date_list and not allow_empty:
        raise Http404
    if make_object_list:
        object_list = queryset.filter(**lookup_kwargs).order_by(date_field)
    else:
        object_list = []
    if not template_name:
        template_name = "%s/%s_archive_year.html" % (model._meta.app_label, model._meta.object_name.lower())
    if this_year:
        template_name= "events_recent.html"
    t = template_loader.get_template(template_name)
    c = RequestContext(request, {
        'date_list': date_list,
        'year': year,
        '%s_list' % template_object_name: object_list,
    }, context_processors)
    for key, value in extra_context.items():
        if callable(value):
            c[key] = value()
        else:
            c[key] = value
    return HttpResponse(t.render(c), mimetype=mimetype)


def updates(request):
    return render_to_response ('updates.html',
                               context_instance = RequestContext (request))


def subscribe_or_return_error(their_email):
    message = ("Subscription request received from the web.")
    recipient = their_email.replace('@', '=')
    recipient = ('rocksoc-official-subscribe-%s@rocksoc.org.uk' % recipient)
    sender = 'webmaster-automated@rocksoc.org.uk'

    if '=' in their_email:
        sender = their_email
        recipient = 'rocksoc-official-subscribe@rocksoc.org.uk'
        # if we ever lose the ability to spoof sender addresses, we'll have to
        # fall back to this:
        #return ("For technical reasons, this form won't work "
        #        "for addresses containing '='. Please send mail "
        #        "to rocksoc-official-subscribe@rocksoc.org.uk "
        #        "or use a different address.")

    try:
        send_mail(subject='Rocksoc mailing list subscription',
                  message=message,
                  from_email=sender,
                  recipient_list=[recipient],
                  fail_silently=False)
    except BadHeaderError:
        mail_admins(subject='BadHeaderError in Rocksoc contact form!',
                    message=("Failed to send to -subscribe because:\n\n"
                             "\t%s" % e),
                    fail_silently=True)
        return ("An email header contained an invalid value. "
                "(If you're trying to break our website: please "
                "don't do that.)")
    except SMTPException, e:
        mail_admins(subject='Failure in Rocksoc contact form!',
                    message=("Failed to send to -subscribe because:\n\n"
                             "\t%s" % e),
                    fail_silently=True)
        return ("Unable to send subscription request at the "
                "moment. Sorry! Please try contacting "
                "<tt>postmaster at rocksoc dot org dot uk</tt>")
    else:
        # \o/
        return ''

from django import forms

class subscribeform(forms.Form):
    your_email = forms.EmailField()
    
def subscribe (request):
    if request.method == 'POST':
        form = subscribeform(request.POST)
        if form.is_valid():
            your_email = form.cleaned_data['your_email']
            error = subscribe_or_return_error(your_email)
            if error:
                errors['your_email'] = [error]
            else:
                return HttpResponseRedirect('/mailing-list/subscribe/ok/')
    else:
        form = subscribeform()
    return render_to_response ('subscribe.html', {
        'form' : form,
    }, context_instance = RequestContext (request))

###########################################

def news(request):
    news_pages = FlatPage.objects.filter(url__startswith="/news/").order_by('url')
    return render_to_response ('news.html', {
        'news_pages' : news_pages,
    }, context_instance = RequestContext (request))

def flatpages_list(request):
    the_flatpages = FlatPage.objects.filter(url__startswith="/r")
    return render_to_response ('flatpages_list.html', {
        'the_flatpages' : the_flatpages,
    }, context_instance = RequestContext (request))

###########################################
# List/Detail views
###########################################

class MemberPhotoList (ListView):
    queryset = MemberPhoto.objects.all ()
    template_name = 'gallery/index_float.html'
    context_object_name = 'photo_list'

class MemberPhotoDetail (DetailView):
    queryset = MemberPhoto.objects.all ()
    template_name = 'gallery/photo.html'
    context_object_name = 'photo'

    def get_context_data (self, **kwargs):
        context = super (MemberPhotoDetail, self).get_context_data (**kwargs)
        context['photo_list'] = MemberPhoto.objects.all ()
        return context

class MinutesList (ListView):
    queryset = Minutes.objects.all ().order_by ('category', '-meeting')
    template_name = 'minutes/index.html'
    context_object_name = 'minutes_list'

class MinutesByCategoryList (ListView):
    template_name = 'minutes/category.html'
    context_object_name = 'minutes_list'

    def get_queryset (self):
        return Minutes.objects.filter (category__tag = self.kwargs['category'])

class MinutesDetail (DetailView):
    queryset = Minutes.objects.all ()
    template_name = 'minutes/minutes.html'
    context_object_name = 'minutes'

class QuoteList (ListView):
    queryset = Quote.objects.all ()
    template_name = 'quotes.html'
    context_object_name = 'quote_list'

class EventFutureList (ListView):
    queryset = Event.objects_in_future.all ()
    template_name = 'events_future.html'
    context_object_name = 'event_list'

    def get_context_data (self, **kwargs):
        context = super (EventFutureList, self).get_context_data (**kwargs)
        context['relevant_years'] = Event.objects_in_past.dates ('edatetime', 'year')
        return context

class VenueDetail (DetailView):
    queryset = Venue.objects.all ()
    template_name = 'venue.html'
    context_object_name = 'venue'
