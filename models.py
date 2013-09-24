# -*- coding: utf-8 -*-

from cStringIO import StringIO
from datetime import datetime, date, timedelta

from django.contrib.sitemaps import Sitemap
from django.db import models
from django import forms
from django.template.defaultfilters import slugify
from django.utils.html import escape

import os
import re

# Try to import PIL in either of the two ways it can end up installed.
try:
    from PIL import Image, ImageEnhance
except ImportError:
    import Image, ImageEnhance


class YNBooleanField(models.BooleanField):
    def to_python(self, value):
        if value in (True, False): return value
        if value == 'Y': return True
        if value == 'N': return False
        raise validators.ValidationError, gettext("This value must be either True or False.")






TEXT_FORMATS = (
    ('text/plain', 'Plain text (no formatting)'),
    ('text/x-rst', 'reStructured Text (see docutils.sf.net)'),
    ('text/x-livejournal', 'HTML with auto line breaks (like Livejournal)'),
    ('application/xhtml+xml', 'XHTML')
)

EVENT_STATUSES = (
    ('FUTURE', 'Active, displayed'),
    ('PAST', 'PAST (no longer useful)'),
    ('REJECTED', 'Rejected, not displayed'),
    ('CANCELLED', 'Cancelled, not displayed'),
)



class Venue(models.Model):
    def __unicode__(self):
        return self.name
#    class Admin:
#        pass
    class Meta:
        ordering = ('id',)
        db_table = "rocksoc_venue"
    name = models.CharField(max_length=50)
    id = models.SlugField(primary_key=True, 
                          #prepopulate_from=('name',),
                          help_text="Used in URLs")
    use_our_page = models.BooleanField(default=False, help_text='True '
                                       'if our DB entry is more '
                                       'informative than their website. '
                                       'If false and there is no website, '
                                       'the venue will not be hyperlinked '
                                       'at all.')
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True, help_text='dont use special characters like &, it breaks the RSS feed')
    map_url = models.URLField("Map URL", blank=True)
    map_image = models.URLField("Inline map image URL", blank=True)
    location = models.TextField(blank=True)
    directions = models.TextField(blank=True, help_text='HTML OK')
    notes = models.TextField(blank=True)


def RrwYnField(*args, **kwargs):
    return models.CharField(max_length=1, choices=(('Y','Yes'),('N','No')), *args, **kwargs)

def RrwQualityField(*a, **kwa):
    return models.CharField(max_length=1, choices=(
            ('0', '0 (worst)'),
            ('1', '1'),
            ('2', '2'),
            ('3', '3'),
            ('4', '4'),
            ('5', '5'),
            ('6', '6'),
            ('7', '7'),
            ('8', '8'),
            ('9', '9 (best)'),
            ('X', 'Unknown/other'),
        ), *a, **kwa)


class Quote(models.Model):
    def __unicode__(self):
        s = self.quote
        if len(s) > 30:
            s = s[:30] + '...'
        return '%s (%s): "%s"' % (self.person, self.date, s)
#    class Admin:
#        list_display = ('date', 'person', 'quote')
#        list_display_links = ('quote',)
    class Meta:
        db_table = "quotes"
        ordering = ('-date',)
    id = models.AutoField(primary_key=True)
    date = models.DateField()
    person = models.CharField(max_length=25)
    quote = models.TextField()
    notes = models.TextField(blank=True, null=True)


class EventsPhotosManager(models.Manager):
    def get_query_set(self):
        return super(EventsPhotosManager, self).get_query_set().filter(epictures__contains='<a ')

class EventsPastManager(models.Manager):
    def get_query_set(self):
        return super(EventsPastManager, self).get_query_set().filter(edatetime__lte=datetime.now())

class EventsFutureManager(models.Manager):
    def get_query_set(self):
        return super(EventsFutureManager, self).get_query_set().filter(edatetime__gte=datetime.now())

class WUSManager(models.Manager):
    def get_query_set(self):
        return super(WUSManager, self).get_query_set().filter(category__tag='wus')

class WUSFutureManager(EventsFutureManager):
    def get_query_set(self):
        return super(WUSFutureManager, self).get_query_set().filter(category__tag='wus')

class WUSPastManager(EventsPastManager):
    def get_query_set(self):
        return super(WUSPastManager, self).get_query_set().filter(category__tag='wus')


class EventCategory(models.Model):
    def __unicode__(self):
        return '%s (%s)' % (self.name, self.tag)
    class Meta:
        verbose_name_plural = 'event categories'
#    class Admin:
#        pass
    name = models.CharField(max_length=100)
    tag = models.SlugField(
                           #prepopulate_from=['name']
                           )


class Event(models.Model):
    def __unicode__(self):
        return '[%s] %s' % (self.edatetime, self.ename)
#    class Admin:
#        save_as=True
#        ordering = ('-edatetime',)
    class Meta:
        ordering = ('edatetime',)
        db_table = 'events'
        verbose_name_plural = 'Events'
        verbose_name = 'Event'
    id = models.AutoField(primary_key=True)
    edatetime = models.DateTimeField('date & time')
    finish_time = models.TimeField('finish time', blank=True, null=True,
            help_text='Finish time (assumed to be <24h after the start time)')
    category = models.ForeignKey(EventCategory, null=True, blank=True)
    ename = models.CharField('name', max_length=100,
        help_text=u'Plain text — use ‘Read More’ link to get a hyperlink')
    elink = models.CharField(u"‘Read More’ link", max_length=100, blank=True,
        help_text=u'Either an absolute link with “http://” or a relative link starting with “/”')
    venue = models.ForeignKey(Venue, null=True)
    edescription = models.TextField('description', blank=True,
        help_text='XHTML: surrounding paragraph tags must be included')
    ereviews = models.TextField('reviews', blank=True, help_text='XHTML (for the links), not currently used')
    epictures = models.TextField('photos', blank=True, help_text='XHTML (for the links)')
    epublicity = models.TextField('publicity', blank=True, help_text='XHTML, not currently used ')
    entered_by = models.CharField(max_length=8, blank=True, help_text='Login or initials, not displayed on the website')
    organised_by = models.CharField(max_length=50, blank=True, help_text='Name of the organiser(s) if not Rocksoc')
    in_cambridge = models.BooleanField('In Cambridge?', default=True)
    eoutlink = models.CharField('Outgoing link', max_length=100, blank=True,
        help_text=u"Appears as a hyperlink on the event’s title")
    eicon = models.CharField('icon', max_length=100, blank=True,
        help_text=u'URL to an image which should be uploaded to “/media/img/events/year”')
    epriority = models.IntegerField('display priority', default=0, help_text='Not currently used')
    eschedule = models.TextField('schedule', blank=True, help_text=u'Something like “Alternate Tuesdays”, not currently used')
    is_rocksoc = models.BooleanField('Official Rocksoc event?', default=False)
    last_modified = models.DateTimeField ('Last modified', auto_now = True, editable = False)

    objects = models.Manager()
    objects_in_past = EventsPastManager()
    objects_in_future = EventsFutureManager()
    objects_with_photos = EventsPhotosManager()
    wuses = WUSManager()
    wuses_in_past = WUSPastManager()
    wuses_in_future = WUSFutureManager()

    def get_absolute_url(self):
        return '/events/%d/#event-%d' % (self.edatetime.year, self.id)

    def get_finish_datetime (self):
        if self.finish_time is None:
            return None

        finish_datetime = datetime.combine (self.edatetime, self.finish_time)

        if finish_datetime < self.edatetime:
            return finish_datetime + timedelta (1) # day

        return finish_datetime

class EventSitemap (Sitemap):
    changefreq = 'weekly'

    def items (self):
        return Event.objects.all ()

    def priority (self, obj):
        if (obj.is_rocksoc):
            return 0.6
        else:
            return 0.4

class WUSDj(models.Model):
    def __unicode__(self):
        return '%s (%s)' % (self.name, self.userid)
#    class Admin:
#        pass
#        list_display = ('name', 'userid')
    class Meta:
        db_table = 'wus_dj'
        ordering = ('name', 'userid')
        verbose_name = 'WUS DJ'
        verbose_name_plural = 'WUS DJs'

    objects = models.Manager()


    def get_sets(self):
        groups = [self] + list(WUSDj.objects.filter(represents_djs=self))
        return WUSSet.objects.filter(dj__in=groups)
    sets = property(get_sets)

    userid = models.SlugField("DJ ID", max_length=20, primary_key=True,
                              help_text="Used in URLs and stuff.",
                              #prepopulate_from=('name',)
                              )
    name = models.CharField("Name", max_length=80,
                            help_text="As it should appear on the website. "
                                      "If it's an alias, put their real name "
                                      "in the contact field")
    plays = models.CharField("Genre played", max_length=80, blank=True,
                             help_text="This will appear on the website.")
    availability = models.CharField(max_length=80, blank=True, help_text="Not shown on the website.")
    inTerm = RrwYnField("Available during term", blank=True, help_text="Not shown on the website.")
    inVacs = RrwYnField("Available outside term", blank=True, help_text="Not shown on the website.")
    represents_djs = models.ManyToManyField('self',
            symmetrical=False, related_name='dj_groups',
            help_text='If this DJ is actually multiple people, the DJ entries '
            'for those people.', 
            #filter_interface=models.HORIZONTAL,
            blank=True, verbose_name='people represented')
    wants_set = RrwYnField(blank=True, help_text="Not shown on the website.")
    request = models.TextField(blank=True, help_text="Not shown on the website.")
    request_date = models.DateTimeField(blank=True, null=True, help_text="Not shown on the website.")
    set_1 = RrwQualityField(default='X', help_text="Not shown on the website.")
    set_2 = RrwQualityField(default='X', help_text="Not shown on the website.")
    set_3 = RrwQualityField(default='X', help_text="Not shown on the website.")
    set_4 = RrwQualityField(default='X', help_text="Not shown on the website.")
    email = models.CharField("Email address", max_length=255, blank=True,
                             help_text="Not shown on the website.")
    contact = models.CharField("Contact details", max_length=255, blank=True,
                             help_text="Not shown on the website.")


    def get_absolute_url(self):
        return '/wus/dj/%s/' % (self.userid)

class WUSDjSitemap (Sitemap):
    changefreq = 'monthly'
    priority = 0.4

    def items (self):
        return WUSDj.objects.all ()


class WUSSet(models.Model):
    def __unicode__(self):
        return '%s %s %s "%s"' % (self.event.edatetime, self.start, self.dj_id, self.playing)
#    class Admin:
#        ordering = ('-id',)
    class Meta:
        ordering = ('event', 'seq',)
        db_table = "wus_wus_set"
        verbose_name = "WUS set"
        #unique_together = (('seq', 'event_id'), ('start', 'event_id'), ('end', 'event_id'))
    event = models.ForeignKey(Event, 
                              #edit_inline=models.TABULAR,
#                              min_num_in_admin=4, num_in_admin=5,
                              related_name='wus_sets')
    start = models.TimeField(
                             #core=True
                             )
    end = models.TimeField(
                           #core=True
                           )
    dj = models.ForeignKey(WUSDj, db_column='dj', to_field='userid',
                           related_name='own_sets', verbose_name='DJ')
    playing = models.CharField("Genre played", max_length=255, blank=True)
    seq = models.IntegerField('Sequence number',
                              help_text='Within that WUS, ordered by time, '
                                        'starting from 0')
    id = models.AutoField(primary_key=True)
    def _get_setlist(self):
        return self.setlist_items.all()
    setlist = property(_get_setlist)

    def get_absolute_url(self):
        return '/wus/date/%s/#%d' % (self.event.edatetime.date(), self.seq)

class WUSSetSitemap (Sitemap):
    changefreq = 'weekly'
    priority = 0.4

    def items (self):
        return WUSSet.objects.all ()

    def lastmod (self, obj):
        return obj.event.last_modified

_RE_NOT_WANTED = re.compile(r'[^-a-zA-Z0-9_]')
_RE_URLIFIED_WHITESPACE = re.compile(r'[-_]+')

def _urlify(s):
    s = s.lower().replace('/', '_').replace(' ', '_').replace('?', '').replace('-', '_')
    s = s.replace("'", '').replace('&', '_and_')
    if s[:4] == 'the_':
        s = s[4:]
    s = _RE_NOT_WANTED.sub('', s)
    s = _RE_URLIFIED_WHITESPACE.sub('_', s)
    s = s.strip('_')
    if not s:
        s = '_'
    return s[:50]


class Artist(models.Model):
#    class Admin:
#        list_display = ('id', 'name')
    class Meta:
        ordering = ['id']
    def __unicode__(self):
        return self.name
    id = models.SlugField('ID (for URLs)', max_length=50, primary_key=True, 
                          #prepopulate_from=('name',)
                          )
    name = models.CharField(max_length=80, unique=True)
    generate_id = staticmethod(_urlify)

    def get_absolute_url(self):
        return '/wus/artist/%s/' % self.id

class ArtistSitemap (Sitemap):
    changefreq = 'monthly'
    priority = 0.3

    def items (self):
        return Artist.objects.all ()


class ArtistAlias(models.Model):
#    class Admin:
#        list_display = ('alias', 'artist')
    class Meta:
        ordering = ['alias']
        verbose_name = 'artist alias'
        verbose_name_plural = 'artist aliases'
    def __unicode__(self):
        return self.alias
    alias = models.CharField(max_length=50, primary_key=True,
                             help_text='Wrong artist ID sometimes seen in URLs')
    artist = models.ForeignKey(Artist, help_text='Replacement artist')

    generate_id = staticmethod(_urlify)


class TrackName(models.Model):
#    class Admin:
#        list_display = ('id', 'name')
    class Meta:
        ordering = ['id']
    def __unicode__(self):
        return self.name
    id = models.SlugField('ID (for URLs)', max_length=50, primary_key=True,
                           #prepopulate_from=('name',)
                           )
    name = models.CharField("Name", max_length=80)
    

    generate_id = staticmethod(_urlify)

    def get_absolute_url(self):
        return '/wus/track/%s/' % self.id

class TrackNameSitemap (Sitemap):
    changefreq = 'monthly'
    priority = 0.3

    def items (self):
        return TrackName.objects.all ()


class TrackAlias(models.Model):
#    class Admin:
#        list_display = ('alias', 'track')
    class Meta:
        ordering = ['alias']
        verbose_name = 'track alias'
        verbose_name_plural = 'track aliases'
    def __unicode__(self):
        return self.alias
    alias = models.CharField(max_length=50, primary_key=True,
                             help_text='Wrong track name in URLs')
    track = models.ForeignKey(TrackName, help_text='Replacement track')

    generate_id = staticmethod(_urlify)


class WUSSetlistItem(models.Model):
#    class Admin:
#        list_display=('set', 'num', 'artist', 'track', 'request')
#        list_filter=('set',)
    class Meta:
        ordering = ['id']
        db_table = 'wus_setlist_item'
        verbose_name = 'WUS setlist item'
        verbose_name_plural = 'WUS setlist items'
    def __unicode__(self):
        return '%s.%s %s - %s' % (self.set_id, self.id,
                                  self.artist.name, self.track.name)
    id = models.AutoField(primary_key=True)
    set = models.ForeignKey(WUSSet, related_name='setlist_items')
                            #, edit_inline=models.TABULAR,
                            #min_num_in_admin=10, num_in_admin=20)
    num = models.IntegerField("Number in set", help_text="Starting from 0")
    artist = models.ForeignKey(Artist, 
                               #core=True, 
                               related_name='setlist_items')
    track = models.ForeignKey(TrackName, 
                              #core=True,
                              related_name='setlist_items')

    song = property(lambda self: self.track.name)
    url_artist = property(lambda self: self.artist_id)
    url_song = property(lambda self: self.track_id)

    def _get_wus(self):
        return self.set.wus
    def _get_wus_id(self):
        return self.set.wus_id
    wus = property(lambda self: self.set.wus)
    wus_id = property(lambda self: self.set.wus_id)

    lp = models.CharField("Album/LP", max_length=80, blank=True)
    track_on_lp = models.IntegerField("Track on album/LP", default=0, help_text="0 means none specified")
    year = models.IntegerField(default=0, help_text="0 means none specified")
    request = models.BooleanField(default=False)

    urlify = staticmethod(_urlify)

    #@classmethod
    def get_top_artists(cls, n=10):
        """Return up to n tuples (Artist, int)."""
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute('''select artist_id, count(artist_id) as c
                        from wus_setlist_item
                        group by artist_id order by c desc limit %d''' % n)
        rows = cursor.fetchall()
        objs = Artist.objects.in_bulk([r[0] for r in rows])
        return [(objs[r[0]], r[1]) for r in rows]
    get_top_artists = classmethod(get_top_artists)

    #@classmethod
    def get_top_tracks(cls, n=10):
        """Return up to n tuples (Artist, TrackName, int)."""
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("""select artist_id, track_id,
                            concat(concat(artist_id, '/'), track_id) as i,
                            count(concat(concat(artist_id, '/'), track_id)) as c
                        from wus_setlist_item
                        group by i order by c desc limit %d""" % n)
        rows = cursor.fetchall()
        aobjs = Artist.objects.in_bulk([r[0] for r in rows])
        tobjs = TrackName.objects.in_bulk([r[1] for r in rows])
        return [(aobjs[r[0]], tobjs[r[1]], r[3]) for r in rows]
    get_top_tracks = classmethod(get_top_tracks)

    #@classmethod
    def get_random_tracks(cls, n=10):
        """Return up to n tuples (Artist, TrackName, play count)."""
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("""select distinct artist_id, track_id,
                            concat(concat(artist_id, '/'), track_id) as i,
                            count(concat(concat(artist_id, '/'), track_id)) as c
                        from wus_setlist_item
                        where track_id <> '_'
                        group by i order by rand()
                        limit %d""" % n)
        rows = cursor.fetchall()
        aobjs = Artist.objects.in_bulk([r[0] for r in rows])
        tobjs = TrackName.objects.in_bulk([r[1] for r in rows])
        return [(aobjs[r[0]], tobjs[r[1]], r[3]) for r in rows]
    get_random_tracks = classmethod(get_random_tracks)


class WUSDjComment(models.Model):
    def __unicode__(self):
        return '%s' % self.ref
    class Meta:
        db_table = 'wus_dj_comments'
        verbose_name = 'WUS DJ comment'
        verbose_name_plural = 'WUS DJ comments'
#    class Admin:
#        list_display = ('author', 'dj', 'made', 'comment', 'ref')
#        ordering= ['-made']
    author = models.CharField(max_length=20, blank=True,
            help_text="Whose comment?")
    dj = models.ForeignKey(WUSDj, related_name='comments', db_column='dj',
                            #edit_inline=models.STACKED, 
                            to_field='userid')
    made = models.DateTimeField()
    comment = models.TextField(
                               #core=True
                               )
    ref = models.AutoField(primary_key=True)


class MinutesCategory(models.Model):
    def __unicode__(self):
        return self.title
    class Meta:
        ordering = ['-id']
        db_table = 'rocksoc_minutes_category'
        verbose_name_plural = 'minutes categories'
#    class Admin:
#        list_display = ('id', 'title', 'description', 'tag')
    id = models.IntegerField('ID', primary_key=True,
                             help_text='Use the beginning year for years, '
                                       'or a small unique number (larger '
                                       'numbers appear first) for AGMs '
                                       'and other special stuff')
    title = models.CharField(max_length=30)
    description = models.CharField(max_length=80, blank=True)
    tag = models.SlugField(help_text='Used in URLs: '
                           'use e.g. 2007-2008 for years', unique=True)


class Minutes(models.Model):
    def __unicode__(self):
        return '%s - %s' % (self.meeting, self.title)
    class Meta:
        db_table = 'rocksoc_minutes'
        ordering = ['-category', '-meeting']
        verbose_name = 'minutes'
        verbose_name_plural = 'minutes'
#    class Admin:
#        ordering = ['-meeting']
#        list_display = ('id', 'meeting', 'title', 'taken_by', 'category')
    id = models.SlugField(primary_key=True,
                           #prepopulate_from=('meeting','title'), 
                           blank=False, null=False, help_text="Should get filled in from the date and title if all goes well. Failing that, use the date or something")
    meeting = models.DateField('meeting date', help_text='YYYY-MM-DD')
    title = models.CharField(max_length=30, blank=True, help_text='If the meeting is in some way special (or there were two on the same day) you can give it a title')
    taken_by = models.CharField(max_length=30, blank=True)
    format = models.CharField(max_length=30, choices=TEXT_FORMATS,
                              default='text/plain')
    minutes = models.TextField()
    category = models.ForeignKey(MinutesCategory)

    def get_absolute_url(self):
        return '/minutes/%s/%s/' % (self.category.tag, self.id)

class MinutesSitemap (Sitemap):
    changefreq = 'monthly'
    priority = 0.4

    def items (self):
        return Minutes.objects.all ()

###############################################################

class JPEGUploadField(forms.FileField):
    def isValidImage(self, field_data, all_data):
        try:
            # Actually you can upload any image ending in .jpeg or .jpg, but
            # don't do that.
            low = field_data['filename'].lower()
            if not low.endswith('.jpg') or low.endswith('.jpeg'):
                raise ValidationError('Please upload a JPEG image '
                                      '(.jpg or .jpeg)')
            if '.' in low[:-5]:
                for ext in ('.cgi.', '.php.', '.sh.', '.pl.', '.py.', '.fcgi.'):
                    if ext in low:
                        raise ValidationError('Please upload an image which '
                                              'does not have multiple '
                                              'extensions')
            size = len(field_data['content'])
            if size > 100 * 1024:
                raise ValidationError('Please upload a JPEG image less than '
                                      '100 KB in size.')

            validators.isValidImage(field_data, all_data)
        except validators.ValidationError, e:
            raise validators.CriticalValidationError, e.messages


class JPEGField(models.ImageField):
    def get_manipulator_field_objs(self):
        return [JPEGUploadField, forms.HiddenField]

class MemberPhoto(models.Model):
    def __unicode__(self):
        return self.caption
    class Meta:
        ordering = ['id']
        db_table = 'rocksoc_member_photos'
        verbose_name = 'Member photo'
        verbose_name_plural = 'Member photos'
#    class Admin:
#        list_display = ('id', 'caption', 'filename')
    id = models.AutoField("ID", primary_key=True)
    caption = models.CharField(max_length=40)
    filename = JPEGField(blank=False, null=False,
                         upload_to='img/members/%Y',
                         width_field='width', height_field='height')
    width = models.PositiveIntegerField(default=0,
            help_text='Automatically recalculated when you upload a new image.')
    height = models.PositiveIntegerField(default=0,
            help_text='Automatically recalculated when you upload a new image.')
    thumbnail = JPEGField(blank=True, upload_to='img/members/120x160/%Y',
            help_text='Automatically regenerated when you upload a new image. '
                      'Must be exactly 120(w)x160(h) for the gallery layout.')

    def get_absolute_url(self):
        return '/gallery/members/%d/' % (self.id)

    def _save_FIELD_file(self, field, filename, raw_contents, save=True):
        super(MemberPhoto, self)._save_FIELD_file(field, filename,
                raw_contents, save)
        os.chmod(self._get_FIELD_filename(field), 0644)
        if field.name == 'filename':
            io = StringIO()
            im = Image.open(self._get_FIELD_filename(field))
            self.width, self.height = im.size
            im.thumbnail((120, 160), Image.ANTIALIAS)
            new = Image.new('RGB', (120, 160), (0,0,0))
            width, height = im.size
            new.paste(im, ((120 - width)/2, (160 - height)/2))
            del im
            new = ImageEnhance.Color(new).enhance(0.0)
            new.save(io, 'JPEG', optimize=True, quality=50)
            new = ImageEnhance.Sharpness(new).enhance(2.0)
            self.save_thumbnail_file(filename, io.getvalue())
            os.chmod(self.get_thumbnail_filename(), 0644)

    def maybe_get_next_by_id(self):
        try:
            return self.__class__.objects.get(id=self.id + 1)
        except self.__class__.DoesNotExist:
            return None

    def maybe_get_prev_by_id(self):
        if self.id == 1:
            return None
        try:
            return self.__class__.objects.get(id=self.id - 1)
        except self.__class__.DoesNotExist:
            return None

    def get_last_by_id(self):
        return self.__class__.objects.order_by('-id')[0]

class MemberPhotoSitemap (Sitemap):
    changefreq = 'yearly'
    priority = 0.3

    def items (self):
        return MemberPhoto.objects.all ()

#########################################################################

class Committee(models.Model):
    def __unicode__(self):
        return self.name
    class Meta:
        db_table = 'rocksoc_committee'
        verbose_name = 'Committee member'
        verbose_name_plural = 'Committee members'
        ordering= ['-year_elected', '-order']
#    class Admin:
#        list_display = ('name','position', 'year_elected')
#        ordering = ['-year_elected', 'order']
    name = models.CharField(max_length=30, blank=False)
    year_elected = models.IntegerField(blank=False)
    position = models.CharField(max_length=30, blank=False)
    email = models.CharField(max_length=30, blank=True, help_text='The bit that comes before the @rocksoc.org.uk')
    order = models.IntegerField(blank=True, help_text='The order the committee members will appear in on the page, President should be 1')
    description = models.TextField(blank=True, help_text="Something witty, can be left blank")
    manifesto = models.TextField (blank = True, help_text = u'The committee member’s manifesto. Can be blank, but preferably not.')
    image = models.CharField(max_length=200, blank=True, help_text='upload images to the media/img/committee/[year] folder on the webspace')

    def get_absolute_url(self):
        return '/committee/%d/#committee-member-%s' % (self.year_elected, slugify (self.name))

class CommitteeSitemap (Sitemap):
    changefreq = 'yearly'
    priority = 0.4

    def items (self):
        return Committee.objects.all ()

    
    
    
