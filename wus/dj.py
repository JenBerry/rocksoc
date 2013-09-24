import sys
from urllib import quote, unquote

from django.http import HttpResponse

from rocksoc._elementtree import Element, SubElement, QName, ElementTree, XML, fill_cell
from rocksoc.cgiutils import guess_unicode
from rocksoc.models import WUSDj, WUSSet, WUS, WUSSetlistItem
from rocksoc.page import RocksocPage
from rocksoc.serializer import serialize_xhtml
from rocksoc.wus.track import fold_track_name, _setlist_tr

HTML_A = 'a'
HTML_P = 'p'
HTML_BR = 'br'
HTML_IMG = 'img'
HTML_DIV = 'div'
HTML_H1 = 'h1'
HTML_H2 = 'h2'
HTML_H3 = 'h3'
HTML_SPAN = 'span'
HTML_TABLE = 'table'
HTML_TR = 'tr'
HTML_TH = 'th'
HTML_TD = 'td'
HTML_UL = 'ul'
HTML_LI = 'li'

def _dj_summary(dj, sets, in_own_page):
    div = Element(HTML_DIV)
    SubElement(div, HTML_H2).text = dj.name
    table = SubElement(div, HTML_TABLE, {'class': 'usersummary', 'width': '100%'})
    tr = SubElement(table, HTML_TR)
    tr.tail = '\n'
    SubElement(tr, HTML_TH, {'class': 'us-name'}).text = 'Name:'
    SubElement(tr, HTML_TD, {'width': '80%', 'class': 'us-value'}).text = dj.name
    if dj.plays:
        tr = SubElement(table, HTML_TR)
        SubElement(tr, HTML_TH, {'class': 'us-name'}).text = 'Plays:'
        SubElement(tr, HTML_TD, {'class': 'us-value'}).text = dj.plays
    tr = SubElement(table, HTML_TR)
    tr.tail = '\n'
    SubElement(tr, HTML_TH, {'class': 'us-name', 'valign': 'top'}).text = 'Sets:'
    sets_cell = SubElement(tr, HTML_TD, {'width': '80%', 'class': 'us-value'})

    counter = 0
    for set in sets:
        try:
            wus = set.wus
        except WUS.DoesNotExist:
            continue
        else:
            date = wus.date_occurs
        if in_own_page:
            a = SubElement(sets_cell, HTML_A, href='#%d'%counter)
        else:
            a = SubElement(sets_cell, HTML_A,
                           href='/wus/dj/%s/#%d'%(set.dj_id, counter))
        a.text = u'%s %s\u2014%s' % (date, str(set.start)[:-3],
                                     str(set.end)[:-3])
        a.tail = ' '
        fill_cell(sets_cell, set.playing)
        SubElement(sets_cell, HTML_BR).tail = '\n'
        counter += 1

    return div

def _all_set_details(dj, sets):
    elts = []

    counter = 0
    for set in sets:
        elts.append(_setlist(dj, set, counter))
        counter += 1
    return elts

def _setlist(dj, set, anchor=None, include_djname=False):
    div = Element(HTML_DIV)

    wus = set.wus

    # Heading
    h2 = SubElement(div, HTML_H2)
    date = wus.date_occurs
    if anchor is not None:
        a = SubElement(h2, HTML_A, name='%s'%anchor, id='%s'%anchor)
    a = SubElement(h2, HTML_A, href='/wus/date/%s/#%d' % (date, set.seq))
    a.text = '%s %s - %s' % (date, set.start, set.end)
    a.tail = ' - '
    fill_cell(h2, set.playing)
    if include_djname:
        h2[-1].tail = (h2[-1].tail or '') + ' ('
        a = SubElement(h2, HTML_A, href='/wus/dj/%s/' % dj.userid)
        a.text = dj.name
        a.tail = ')'
    h2.tail = '\n'

    # Body
    rows = list(set.setlist)
    if len(rows) < 1:
        SubElement(div, HTML_DIV).text = 'No setlist information available for this set';
    else:
        table = SubElement(div, HTML_TABLE)
        table.tail = '\n'
        for row in rows:
            table.append(_setlist_tr(row))
    return div

def handle_wus_dj_index(path):
    h1 = Element(HTML_H1)
    img = SubElement(h1, HTML_IMG, src='/wus/logo-674x70.png', width='674', height='70')
    img.tail = 'DJs list'

    # Sorted by name using something resembling a Schwartzian transform
    temp = []

    p = Element(HTML_P)
    p.text = 'Any Rocksoc member can ask to DJ at Wake Up Screaming: see the '
    a = SubElement(p, HTML_A, href='/wus/djinfo/')
    a.text = 'DJ Information page'
    a.tail = ' for more details.'
    temp.append(('', p))        # '' sorts before everything

    for dj in WUSDj.objects.all():
        sets = dj.sets.order_by('-wus')
        if sets.count():
            temp.append((dj.name, _dj_summary(dj, sets, False)))

    temp.sort()
    content = [x[1] for x in temp]
    del temp

    return RocksocPage(path, 'Wake Up Screaming: ' + img.tail, *content)

def handle_wus_dj(path, path_info):
    userid = path_info
    if userid[0:1] == '/':
        userid = userid[1:]
    if userid[-1:] == '/':
        userid = userid[:-1]
    userid = unquote(userid)

    if userid == '':
        handle_wus_dj_index(path)
        raise SystemExit(0)

    h1 = Element(HTML_H1)
    SubElement(h1, HTML_IMG, src='/wus/logo-674x70.png', width='674', height='70', alt='Wake Up Screaming')
    subtitle = SubElement(h1, HTML_BR)

    try:
        dj = WUSDj.objects.get(userid__exact=userid)
    except (LookupError, WUSDj.DoesNotExist):
        subtitle.tail = 'DJ not known: %s' % userid
        content = (h1, Element(HTML_P),)
        content[1].text = 'There is no DJ with that ID in our database.'
        status_text = 'Not Found'
        status = 404
    else:
        sets = dj.sets.order_by('-wus')
        subtitle.tail = 'DJ info: %s' % dj.name
        content = ((h1, _dj_summary(dj, sets, True))
                   + tuple(_all_set_details(dj, sets)))
        status_text = 'OK'
        status = 200

    page = RocksocPage(path, 'Wake Up Screaming: ' + subtitle.tail, *content)
    return page, status, status_text

def dj_view(request, path_info):
    page, status, status_text = handle_wus_dj('', path_info)
    resp = HttpResponse(mimetype='text/html; charset=utf-8')
    resp['Status'] = '%3.3d %s' % (status, status_text)
    resp['X-Powered-By'] = 'Django'
    serialize_xhtml(page, resp, 'utf-8')
    resp.write('<!--Powered by Django-->\n')
    return resp

def index_view(request):
    page = handle_wus_dj_index('')
    resp = HttpResponse(mimetype='text/html; charset=utf-8')
    resp['X-Powered-By'] = 'Django'
    serialize_xhtml(page, resp, 'utf-8')
    resp.write('<!--Powered by Django-->\n')
    return resp

# vim:set sw=4 sts=4 et:
