#!/usr/bin/python2.3

import os
import sys
os.environ['DJANGO_SETTINGS_MODULE'] = 'rocksoc.settings'
sys.path[:0] = ['/home/rocksoc/www/lib/python2.5/site-packages',
                '/home/rocksoc/www/libpython']

import re
from datetime import date as Date, time as Time
from md5 import md5

from rocksoc.models import WUSSet, WUSSetlistItem, Artist, TrackName

from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.cache import never_cache
import django.forms as forms
from django.utils import encoding

# Accept anything like one of these:
# Iron Maiden - Aces High
# 3. Iron Maiden - Aces High [Powerslave]
# Iron Maiden - Aces High [track 1, Powerslave]
# Iron Maiden - Aces High [Powerslave, 1995]
# Iron Maiden - Aces High [track 1, Powerslave, 1995]

# If the line is a request, match with the request part in group 2, and the
# rest (to be matched against TRAD_SETLIST_LINE) in group 1.
TRAD_SETLIST_REQUEST = re.compile(r'^\s*(.+?)\s+[[(](r|request|track request|band request|artist request|song request)[])]\s*$', re.I)
# If the line is a traditional setlist line (with request suffix removed),
# match the number in set (if any) in group 1, the artist in group 2,
# the track in group 3, the track number on the album (if any) in group 4,
# the name of the album (if any) in group 5, and the year (if any) in group 6.
TRAD_SETLIST_LINE = re.compile(r'^\s*(?:(\d+)\.\s+)?(.+?)\s+-\s+(.+?)(?:\s+\[(?:track\s+(\d+),\s+)?(.*?)(?:,\s+((?:19|20)\d\d))?\])?\s*$', re.I)

class SetlistItem(object):

    def __init__(self, set_obj, n_so_far):
        self.set_obj = set_obj
        self.num = 0
        self.artist = ''
        self.title = ''
        self.lp = ''
        self.track_on_lp = 0
        self.year = 0
        self.request = 0
        self.n_so_far = n_so_far

    def enter(self, preview_actions=None):
        try:
            a_obj = Artist.objects.get(name=self.artist)
        except Artist.DoesNotExist:
            a_id = Artist.generate_id(self.artist)
            if preview_actions is None:
                a_obj, unused = Artist.objects.get_or_create(id=a_id,
                                                             defaults={'name': self.artist})
            else:
                preview_actions.append('Will create new artist "%s" with ID '
                                       '"%s"' % (self.artist, a_id))

        try:
            t_obj = TrackName.objects.get(name=self.title)
        except TrackName.DoesNotExist:
            t_id = TrackName.generate_id(self.title)
            if preview_actions is None:
                t_obj, unused = TrackName.objects.get_or_create(id=t_id,
                                                                defaults={'name': self.title})
            else:
                preview_actions.append('Will create new track name "%s" with '
                                       'ID "%s"' % (self.title, t_id))

        if not self.num:
            # auto-number
            self.num = self.n_so_far + 1

        if preview_actions is None:
            i = WUSSetlistItem(set=self.set_obj, num=self.num-1,
                               artist_id=a_obj.id, track_id=t_obj.id,
                               lp=self.lp, track_on_lp=self.track_on_lp,
                               year=self.year, request=self.request)
            i.save()

    def __unicode__(self):
        base = '%d. %s - %s' % (self.num, self.artist, self.title)
        if self.lp:
            base += ' ['
            if self.track_on_lp:
                base += 'track %d, ' % self.track_on_lp
            base += self.lp
            if self.year:
                base += ', %d' % self.year
            base += ']'
        if self.request:
            base += ' (request)'
        return base

    def load_trad_line(self, line):
        m = TRAD_SETLIST_REQUEST.match(line)
        if m:
            self.request = 1
            line = m.group(1)
        m = TRAD_SETLIST_LINE.match(line)
        if not m:
            raise ValueError(line)
        self.num = int(m.group(1) or 0)
        self.artist = m.group(2) or ''
        self.title = m.group(3) or ''
        self.track_on_lp = int(m.group(4) or 0)
        self.lp = m.group(5) or ''
        self.year = int(m.group(6) or 0)

def format_item(self):
    base = '%d. %s - %s' % (self.num + 1, self.artist.name, self.track.name)
    if self.lp:
        base += ' ['
        if self.track_on_lp:
            base += 'track %d, ' % self.track_on_lp
        base += self.lp
        if self.year:
            base += ', %d' % self.year
        base += ']'
    if self.request:
        base += ' (request)'
    return base

class SetlistEntry(forms.Form):
    temp = forms.CharField(required=False, widget = forms.HiddenInput)
#    md5 = forms.IntegerField(required=False, widget = forms.HiddenInput)
    setlist = forms.CharField(required=False, widget = forms.Textarea)

# vim:set sw=4 sts=4 et:
