from django.views.generic.detail import DetailView

from rocksoc.models import Artist

"""
The detail view of a particular WUS artist at http://www.rocksoc.org.uk/wus/artist/artist-name/
"""
class WusArtistDetailView (DetailView):
    queryset = Artist.objects.all ()
    template_name = 'wus/artist.html'
    context_object_name = 'artist'

    def get_context_data (self, **kwargs):
        context = super (WusArtistDetailView, self).get_context_data (**kwargs)
        context.update ({
            'artist_on_own_page' : True
        })

        return context
