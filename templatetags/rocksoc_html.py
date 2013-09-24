import re

from django import template
from django.utils.html import escape, linebreaks
from django.template.defaultfilters import linebreaksbr
from django.contrib.markup.templatetags.markup import restructuredtext

register = template.Library()

def times(value):
    value = int(value)
    if value == 1:
        return 'once'
    if value == 2:
        return 'twice'
    return '%d times' % value

MODELINE = re.compile('(?:(?:^|[ \r\n\t])vim?|[ \t]ex:)set? ([^:]+):')

def format_flatpage(flatpage):
    value = flatpage.content

    format = flatpage.format
    if format == 'application/xhtml+xml':
        return value
    elif format == 'text/x-livejournal':
        return linebreaks(value)
    elif format == 'text/x-rst':
        return restructuredtext(value)
    else: # format == 'text/plain':
        return linebreaks(escape(value))

def listexclude(x, exc):
    x = list(x)
    return [a for a in x if a != exc]

register.filter('times', times)
register.filter('format_flatpage', format_flatpage)
register.filter('listexclude', listexclude)

# vim:set sw=4 sts=4 et:
