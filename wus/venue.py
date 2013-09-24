import os
import sys
from urllib import quote, unquote

from django.http import HttpResponse

from rocksoc.models import Venue

def handle_wus_venue(path, path_info):
    h1 = Element(HTML_H1)

    placeid = path_info
    if placeid[0:1] == '/':
        placeid = placeid[1:]
    if placeid[-1:] == '/':
        placeid = placeid[:-1]
    placeid = unquote(placeid).lower()
    if placeid.startswith('the '):
        placeid = placeid[4:]

    if placeid.startswith('venue-') and placeid.endswith('.html'):
        placeid = placeid[6:][:-5]
        sys.stdout.write('Status: 302 Moved\r\n')
        sys.stdout.write('Location: http://%s/wus/venue/%s\r\n' % (get_self_uri_authority(),
                                                                   placeid))
        sys.stdout.write('\r\n')

    rows = Venue.objects.filter(id__exact=placeid)
    if rows.count() < 1:
        h1.text = 'Venue not known: %s' % placeid
        content = (h1, Element(HTML_P),)
        content[1].text = 'There is no venue with that ID in our database.'
        status_text = 'Not Found'
        status = 404
    else:
        venue = rows[0]     # must be unique, in fact
        h1.text = 'Venue: %s' % venue.name
        content = [h1]
        if venue.location:
            h2 = Element(HTML_H2)
            h2.text = '%s, %s' % (venue.name, venue.location)
            h2.tail = '\n'
            content.append(h2)
        table = Element(HTML_TABLE, {'class': 'venuetable', 'width': '100%'})
        if venue.map_url:
            tr = SubElement(table, HTML_TR)
            tr.tail = '\n'
            th = SubElement(tr, HTML_TH)
            th.text = 'Map:'
            td = SubElement(tr, HTML_TD)
            a = SubElement(td, HTML_A, href=venue.map_url)
            if venue.map_image:
                uri = venue.map_image
                SubElement(a, HTML_IMG, src=uri, alt='click here for a map')
            else:
                a.text = 'click here for a map'
        if venue.directions:
            tr = SubElement(table, HTML_TR)
            tr.tail = '\n'
            th = SubElement(tr, HTML_TH)
            th.text = 'Directions:'
            td = SubElement(tr, HTML_TD)
            fill_cell(td, venue.directions)
        if venue.phone:
            tr = SubElement(table, HTML_TR)
            tr.tail = '\n'
            th = SubElement(tr, HTML_TH)
            th.text = 'Phone:'
            td = SubElement(tr, HTML_TD)
            td.text = venue.phone
        if venue.website:
            tr = SubElement(table, HTML_TR)
            tr.tail = '\n'
            th = SubElement(tr, HTML_TH)
            th.text = 'Website:'
            td = SubElement(tr, HTML_TD)
            a = SubElement(td, HTML_A, href=venue.website)
            a.text = venue.website
        # don't display email until I think of a good way to handle it...
        if venue.notes:
            tr = SubElement(table, HTML_TR)
            tr.tail = '\n'
            th = SubElement(tr, HTML_TH)
            th.text = 'Notes:'
            td = SubElement(tr, HTML_TD)
            td.text = venue.notes
        content.append(table)

        status_text = 'OK'
        status = 200

    page = RocksocPage(path, h1.text, *content)
    return page, status, status_text

def details_view(request, path_info):
    page, status, status_text = handle_wus_venue('', path_info)
    resp = HttpResponse(mimetype='text/html; charset=utf-8')
    resp['Status'] = '%3.3d %s' % (status, status_text)
    resp['X-Powered-By'] = 'Django'
    serialize_xhtml(page, resp, 'utf-8')
    resp.write('<!--Powered by Django-->\n')
    return resp

# vim:set sw=4 sts=4 et:
