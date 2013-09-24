from rocksoc.models import Venue, Quote, EventCategory, Event, WUSDj, WUSSet, Artist, ArtistAlias, TrackName, TrackAlias, WUSSetlistItem, WUSDjComment, MinutesCategory, Minutes, Committee, MemberPhoto
from rocksoc.wus.enter_setlist import SetlistEntry, format_item, SetlistItem
from django.contrib import admin, auth
from django.contrib.admin import sites, helpers
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import User, Group
from django.contrib.sites.models import Site
from django.contrib.sites.admin import SiteAdmin
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _
from django.http import Http404, HttpResponse, HttpResponseRedirect
from rocksoc.flatpages.admin import FlatPageOptions
from rocksoc.flatpages.models import FlatPage

class WUSSet_Inline(admin.TabularInline):
    model = WUSSet
    extra = 5

class WUSSetlistItem_Inline(admin.TabularInline):
    model = WUSSetlistItem
    extra = 20

class WUSDjComment_Inline(admin.StackedInline):
    model = WUSDjComment

class MinutesCategoryOptions(admin.ModelAdmin):
    list_display = ('id', 'title', 'description', 'tag')

class WUSDjCommentOptions(admin.ModelAdmin):
    list_display = ('author', 'dj', 'made', 'comment', 'ref')
    ordering= ['-made']

class WUSSetlistItemOptions(admin.ModelAdmin):
    list_display=('set', 'num', 'artist', 'track', 'request')
    search_fields = ['artist__name', 'track__name']

class WUSDjOptions(admin.ModelAdmin):
    inlines = [WUSDjComment_Inline]
    list_display = ('name', 'userid')
    prepopulated_fields = {'userid': ('name',)}
    filter_horizontal = ('represents_djs',)

class QuoteOptions(admin.ModelAdmin):
    list_display = ('date', 'person', 'quote')
    list_display_links = ('quote',)

class TrackAliasOptions(admin.ModelAdmin):
    list_display = ('alias', 'track')

class ArtistOptions(admin.ModelAdmin):
    list_display = ('id', 'name')
    prepopulated_fields = {'id': ('name',)}
    search_fields = ['id', 'name']

class VenueOptions(admin.ModelAdmin):
    prepopulated_fields = {'id': ('name',)}

class WUSSetOptions(admin.ModelAdmin):
    inlines = [WUSSetlistItem_Inline]
    ordering = ('-id',)
    list_display=('event','dj', 'start', 'end')
    #search_fields = ['event', 'dj']
    #list_filter = ('start')
    change_form_template = 'wus/setlist_form.html'

    def change_view (self, request, set_id, form_url = '', extra_context = None):
        try:
            set = WUSSet.objects.get (pk = set_id)
        except Event.DoesNotExist:
            raise Http404 ()

        if not self.has_change_permission(request, set):
            raise PermissionDenied

        if request.method == 'GET':
            new_data = request.GET.copy()
        elif request.method == 'POST':
            new_data = request.POST.copy()
        else:
            new_data = {}

        setlist = new_data.get('setlist', '')
        previous_submission = new_data.get('temp', '')
        temp = setlist

        items = []
        preview = []
        complaints = []

        if setlist:
            n_so_far = 0
            for line in setlist.splitlines():
                if line.strip():
                    s = SetlistItem(set, n_so_far)
                    n_so_far += 1
                    try:
                        s.load_trad_line(line)
                    except ValueError:
                        complaints.append('Unable to understand line: %s' % line)
                    items.append(s)

            if request.method == 'POST' and temp == previous_submission \
                    and not complaints:
                set.setlist_items.all().delete()
                for s in items:
                    s.enter()
                return HttpResponseRedirect(set.get_absolute_url())
            else:
                for s in items:
                    s.enter(preview_actions=preview)
        else:
            setlist = '\n'.join([format_item(i) for i in set.setlist_items.all()])
            temp = setlist

        # Now we've given them a preview, they can accept it if they want
        new_data = {'setlist': setlist,
                    'temp': temp}

        form = SetlistEntry(new_data)
        adminForm = helpers.AdminForm(form, self.get_fieldsets(request, set),
            self.get_prepopulated_fields(request, set),
            self.get_readonly_fields(request, set),
            model_admin=self)
        media = self.media + adminForm.media

        context = {
            'title' : 'Change WUS set list',
            'form' : form,
            'actions' : preview,
            'complaints' : complaints,
            'set' : set,
            'items' : items,
            'app_label': self.opts.app_label,
            'adminform': adminForm,
            'object_id': set_id,
            'original': set,
            'media': media,
        }
        context.update(extra_context or {})
        return self.render_change_form(request, context, change=True, obj=set, form_url=form_url)

class ArtistAliasOptions(admin.ModelAdmin):
    list_display = ('alias', 'artist')

class MinutesOptions(admin.ModelAdmin):
    ordering = ['-meeting']
    list_display = ('id', 'meeting', 'title', 'taken_by', 'category')
    prepopulated_fields = {'id': ('meeting','title')}

class TrackNameOptions(admin.ModelAdmin):
    list_display = ('id', 'name')
    prepopulated_fields = {'id': ('name',)}
    search_fields = ['id', 'name']

class CommitteeOptions(admin.ModelAdmin):
    list_display = ('name','position', 'year_elected')
    ordering = ['-year_elected', 'order']

class EventOptions(admin.ModelAdmin):
    list_display = ('edatetime','ename', 'category', 'is_rocksoc')
    list_filter  = ('category', 'is_rocksoc')
    inlines = [WUSSet_Inline]
    save_as=True
    ordering = ('-edatetime',)

class MemberPhotoOptions(admin.ModelAdmin):
    list_display = ('caption', 'filename')

# Create a new AdminSite with the name "leeroy" (rather than "admin", so that we don't get script-kiddie attacks)
site = sites.AdminSite ('leeroy')

# Custom models
site.register (MinutesCategory, MinutesCategoryOptions)
site.register (WUSDjComment, WUSDjCommentOptions)
site.register (WUSSetlistItem, WUSSetlistItemOptions)
site.register (WUSDj, WUSDjOptions)
site.register (Quote, QuoteOptions)
site.register (TrackAlias, TrackAliasOptions)
site.register (Artist, ArtistOptions)
site.register (Venue, VenueOptions)
site.register (WUSSet, WUSSetOptions)
site.register (ArtistAlias, ArtistAliasOptions)
site.register (Minutes, MinutesOptions)
site.register (TrackName, TrackNameOptions)
site.register (EventCategory)
site.register (Committee, CommitteeOptions)
site.register (Event, EventOptions)
site.register (MemberPhoto, MemberPhotoOptions)

site.register (FlatPage, FlatPageOptions)

# Django's stock user management (django.contrib.auth.admin)
site.register (Group, GroupAdmin)
site.register (User, UserAdmin)

# Other stock Django admin models
site.register (Site, SiteAdmin)
