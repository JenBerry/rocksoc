from django.views.generic.detail import DetailView

from rocksoc.models import TrackName

"""
The detail view of a particular WUS track at http://www.rocksoc.org.uk/wus/track/track-name/
"""
class WusTrackDetailView (DetailView):
    queryset = TrackName.objects.all ()
    template_name = 'wus/track.html'
    context_object_name = 'track'

    def get_context_data (self, **kwargs):
        context = super (WusTrackDetailView, self).get_context_data (**kwargs)
        context.update ({
            'track_on_own_page' : True
        })

        return context
