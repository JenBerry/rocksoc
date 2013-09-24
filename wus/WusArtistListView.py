from django.views.generic import ListView
from django import forms

from rocksoc.models import Artist
from rocksoc.NamePaginator import NamePaginator

class WusArtistSearchForm (forms.Form):
    s = forms.CharField (label = 'Artist name', max_length = 100, required = False)

"""
The list view of WUS artists at http://www.rocksoc.org.uk/wus/artist/
"""
class WusArtistListView (ListView):
    template_name = 'wus/artist_index.html'
    context_object_name = 'artist_list'
    paginate_by = 10
    paginator_class = NamePaginator

    def get_queryset (self):
        search_form = WusArtistSearchForm (self.request.GET)
        if search_form.is_valid ():
            search_terms = search_form.cleaned_data['s']
            if search_terms != '':
                return Artist.objects.filter (name__icontains = search_terms)

        return Artist.objects.all ()

    def get_context_data (self, **kwargs):
        context = super (WusArtistListView, self).get_context_data (**kwargs)
        context.update ({
            'search_form' : WusArtistSearchForm (self.request.GET),
            'search_terms' : self.request.GET.get ('s', '')
        })

        return context
