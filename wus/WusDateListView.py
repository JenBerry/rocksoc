from django.views.generic import ListView

from rocksoc.models import Event

"""
The listing of all WUS events by date at http://www.rocksoc.org.uk/wus/date/
"""
class WusDateListView (ListView):
    queryset = Event.wuses.all ().order_by ('-edatetime')
    template_name = 'wus/date_index.html'
    paginate_by = 10
    context_object_name = 'wus_list'

    def get_context_data (self, **kwargs):
        context = super (WusDateListView, self).get_context_data (**kwargs)
        context.update ({
            'wus_summary_years' : True
        })

        return context
