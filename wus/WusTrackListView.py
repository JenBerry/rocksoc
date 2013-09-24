from django.views.generic import ListView
from django import forms

from rocksoc.models import TrackName
from rocksoc.NamePaginator import NamePaginator

class WusTrackSearchForm (forms.Form):
    s = forms.CharField (label = 'Track name', max_length = 100, required = False)

"""
The list view of WUS tracks at http://www.rocksoc.org.uk/wus/track/
"""
class WusTrackListView (ListView):
    template_name = 'wus/track_index.html'
    context_object_name = 'track_list'
    paginate_by = 10
    paginator_class = NamePaginator

    def get_queryset (self):
        search_form = WusTrackSearchForm (self.request.GET)
        if search_form.is_valid ():
            search_terms = search_form.cleaned_data['s']
            if search_terms != '':
                return TrackName.objects.filter (name__icontains = search_terms)

        return TrackName.objects.all ()

    def get_context_data (self, **kwargs):
        context = super (WusTrackListView, self).get_context_data (**kwargs)
        context.update ({
            'search_form' : WusTrackSearchForm (self.request.GET),
            'search_terms' : self.request.GET.get ('s', '')
        })

        return context
