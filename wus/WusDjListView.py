from django.views.generic import ListView

from rocksoc.models import WUSDj
from rocksoc.NamePaginator import NamePaginator

"""
The listing of all WUS DJs by name at http://www.rocksoc.org.uk/wus/dj/
"""
class WusDjListView (ListView):
    queryset = WUSDj.objects.all ()
    template_name = 'wus/dj_index.html'
    paginate_by = 10
    paginator_class = NamePaginator
    context_object_name = 'dj_list'
