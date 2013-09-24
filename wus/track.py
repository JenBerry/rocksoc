import sys
from urllib import quote, unquote

from django.http import HttpResponse

from rocksoc._elementtree import Element, SubElement, QName, ElementTree, XML, fill_cell

from rocksoc.cgiutils import guess_unicode
from rocksoc.page import RocksocPage
from rocksoc.serializer import serialize_xhtml
from rocksoc.models import WUSSetlistItem, WUS, WUSUser, WUSSet

fold_track_name = WUSSetlistItem.urlify

HTML_A = 'a'
HTML_BR = 'br'
HTML_DIV = 'div'
HTML_EM = 'em'
HTML_H1 = 'h1'
HTML_H2 = 'h2'
HTML_IMG = 'img'
HTML_LI = 'li'
HTML_P = 'p'
HTML_SPAN = 'span'
HTML_TABLE = 'table'
HTML_TD = 'td'
HTML_TH = 'th'
HTML_TR = 'tr'
HTML_UL = 'ul'

def _list_plays(plays):
    table = Element(HTML_TABLE, {'class': 'plays-of'})
    table.text = '\n'
    table.tail = '\n'
    for p in plays:
        set = p.set
        userid = set.dj.userid
        djname = set.dj.name
        date = p.wus.date_occurs
        tr = SubElement(table, HTML_TR)
        tr.tail = '\n'
        td = SubElement(tr, HTML_TD, {'class': 'datetime'})
        a = SubElement(td, HTML_A, href='/wus/date/%s/#%d' % (date, set.seq))
        a.text = '%s %s - %s' % (date, str(set.start)[:-3], str(set.end)[:-3])
        td = SubElement(tr, HTML_TD, {'class': 'dj'})
        a = SubElement(td, HTML_A, href='/wus/dj/%s/' % userid)
        a.text = djname
        td = SubElement(tr, HTML_TD, {'class': 'genre'})
        fill_cell(td, set.playing)
        table.append(_setlist_tr(p))
    return (table,)

def _setlist_tr(p):
    tr = Element(HTML_TR)
    tr.tail = '\n'
    td = SubElement(tr, HTML_TD, {'colspan': '3', 'class': 'song'})
    td.text = '%s. ' % (p.num+1)
    a = SubElement(td, HTML_A, href='/wus/artist/%s/'
                          % quote(p.artist.id, ''))
    a.text = guess_unicode(p.artist.name)
    a.tail = ' - '
    a = SubElement(td, HTML_A, href='/wus/track/%s/'
                          % quote(p.track.id, ''))
    a.text = guess_unicode(p.track.name)
    if p.request:
        a.tail = ' '
        SubElement(td, HTML_SPAN, {'class': 'request'}).text = '(Request)'
    if p.lp:
        a.tail = (a.tail or '') + ' ['
        em = SubElement(td, HTML_EM, {'class': 'albumname'})
        em.text = guess_unicode(p.lp)
        em.tail = ''
        if p.year:
            em.tail += ', %s' % p.year
        if p.track_on_lp:
            a.tail += 'track %d, ' % p.track_on_lp
        em.tail += ']'
    return tr

def page_track_or_artist(path, path_info, do_track):
    if do_track:
        item = 'track'
        cap_word = 'Track'
        word = 'track'
    else:
        item = 'artist'
        cap_word = 'Artist'
        word = 'artist'

    ident = path_info
    if ident[0:1] == '/':
        ident = ident[1:]
    if ident[-1:] == '/':
        ident = ident[:-1]
    ident = fold_track_name(unquote(ident))
    if ident.startswith('the_'):
        ident = ident[4:]

    h1 = Element(HTML_H1)
    SubElement(h1, HTML_IMG, src='/wus/logo-674x70.png', width='674', height='70', alt='Wake Up Screaming')
    subtitle = SubElement(h1, HTML_BR)

    plays = WUSSetlistItem.objects.filter(**{'%s__id__exact' % item: ident})
    if plays.count() < 1:
        subtitle.tail = '%s not known: %s' % (cap_word, guess_unicode(ident))
        content = (h1, Element(HTML_P),)
        content[1].text = ('There is no %s with that name in our database.'
                           % word)
        status_text = 'Not Found'
        status = 404
    else:
        if do_track:
            subtitle.tail = 'Plays for %s' % guess_unicode(plays[0].track.name)
        else:
            subtitle.tail = 'Songs by %s' % guess_unicode(plays[0].artist.name)
        content = (h1,) + tuple(_list_plays(plays))
        status_text = 'OK'
        status = 200

    return (RocksocPage(path, 'Wake Up Screaming: ' + subtitle.tail, *content),
            status, status_text)

def handle_track_or_artist(path, path_info, do_track):
    page, status, status_text = page_track_or_artist(path, path_info, do_track)

    sys.stdout.write('Content-Type: text/html; charset=utf-8\r\n'
                     'Status: %3.3d %s\r\n'
                     '\r\n' % (status, status_text))
    try:
        serialize_xhtml(page, sys.stdout, 'utf-8')
        sys.stdout.write('<!--Not powered by Django-->')
    except IOError, e:
        if e[0] != EPIPE:
            raise
    raise SystemExit(0)

def artist_view(request, path_info):
    page, status, status_text = page_track_or_artist('', path_info, False)
    resp = HttpResponse(mimetype='text/html; charset=utf-8')
    resp['Status'] = '%3.3d %s' % (status, status_text)
    resp['X-Powered-By'] = 'Django'
    serialize_xhtml(page, resp, 'utf-8')
    resp.write('<!--Powered by Django-->\n')
    return resp

def track_view(request, path_info):
    page, status, status_text = page_track_or_artist('', path_info, True)
    resp = HttpResponse(mimetype='text/html; charset=utf-8')
    resp['Status'] = '%3.3d %s' % (status, status_text)
    resp['X-Powered-By'] = 'Django'
    serialize_xhtml(page, resp, 'utf-8')
    resp.write('<!--Powered by Django-->\n')
    return resp

# vim:set ft=python sts=4 sw=4 et:
