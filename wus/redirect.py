from datetime import date
from urllib import unquote_plus

from django.http import HttpResponseRedirect, Http404

from rocksoc.models import WUSSetlistItem, ArtistAlias, TrackAlias, Event

def tracksbyartist(request, pi):
    if pi[:1] == '/':
        pi = pi[1:]

    if pi.startswith('tracksbyartist-'):
        pi = pi[len('tracksbyartist-'):]
    if pi.endswith('.html'):
        pi = pi[:-5]
    name = unquote_plus(pi).lower().replace('\\', '')
    if name.startswith('-'):
        name = name[1:]

    cpts = name.split('-')
    if len(cpts) == 2:
        # for now we ignore the artist name and search by song only
        name = WUSSetlistItem.urlify(cpts[1])

    name = WUSSetlistItem.urlify(name)

    # first see if it's an artist - desirable for bands with self-titled songs
    # (Iron Maiden, Motorhead, Conquest of Steel)
    # we still have a problem with e.g. Alice Cooper - Poison vs the band
    # Poison, but there's nothing we can do about that

    entries = ArtistAlias.objects.filter(alias__exact=name)
    if entries.count() > 0:
        return HttpResponseRedirect('/wus/artist/%s/' % entries[0].artist_id)

    plays = WUSSetlistItem.objects.filter(artist__id__exact=name)
    if plays.count() > 0 and len(cpts) != 2:
        return HttpResponseRedirect('/wus/artist/%s/' % name)

    # not an artist, perhaps it's a track?
    entries = TrackAlias.objects.filter(alias__exact=name)
    if entries.count() > 0:
        return HttpResponseRedirect('/wus/track/%s/' % entries[0].track_id)

    plays = WUSSetlistItem.objects.filter(track__id__exact=name)
    if plays.count() > 0:
        return HttpResponseRedirect('/wus/track/%s/' % name)

    raise Http404

# vim:set sw=4 sts=4 et ft=python:
