from django.views.generic.dates import DayArchiveView

from rocksoc.models import Event

"""
The detail view of a particular WUS event at http://www.rocksoc.org.uk/wus/date/yyyy-mm-dd/
"""
class WusDateDetailView (DayArchiveView):
    queryset = Event.wuses.all ()
    template_name = 'wus/date.html'
    context_object_name = 'wus_list'
    allow_future = True
    month_format = '%m'
    allow_empty = False
    date_field = 'edatetime'
