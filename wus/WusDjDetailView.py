from django.views.generic.detail import DetailView

from rocksoc.models import WUSDj

"""
The detail view of a particular WUS DJ at http://www.rocksoc.org.uk/wus/dj/dj-name/
"""
class WusDjDetailView (DetailView):
    queryset = WUSDj.objects.all ()
    template_name = 'wus/dj.html'
    context_object_name = 'dj'

    def get_context_data (self, **kwargs):
        context = super (WusDjDetailView, self).get_context_data (**kwargs)
        context.update ({
            'dj_on_own_page' : True
        })

        return context
