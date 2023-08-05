import os
import re

from zope.i18n.interfaces import IUserPreferredLanguages

from fanstatic import Library, Resource

from js import jqueryui

library = Library('horae.datetime', 'static')

spinbox = Resource(library, 'jquery.spinbox.js', depends=[jqueryui.jqueryui, ])
css = Resource(library, 'datetime.css')
js = Resource(library, 'datetime.js', depends=[spinbox, ])


def find_available_jqueryui_languages():
    avail = {}
    path = os.path.join(os.path.sep.join(jqueryui.__path__), 'resources', 'ui', 'i18n')
    regex = re.compile(r'^jquery\.ui\.datepicker-([a-z]{2}-?[A-Z]{0,2})\.js$')
    files = os.listdir(path)
    for file in files:
        match = regex.match(file)
        if match:
            avail[match.group(1)] = file
    return avail
jqueryui_available = find_available_jqueryui_languages()


def jqueryui_i18n(request):
    # find preferred jquery ui i18n file
    langs = IUserPreferredLanguages(request).getPreferredLanguages()
    avail = jqueryui_available.keys()
    l = None
    for l in langs:
        if l[:2] == 'en':
            l = None
            break
        if l in avail:
            break
        if len(l) > 2:
            if '-'.join([l[:2], l[3:].upper()]) in avail:
                l = '-'.join([l[:2], l[3:].upper()])
                break
            if l[:2] in avail:
                l = l[:2]
                break
    if l is not None:
        return Resource(jqueryui.library, os.path.join('ui', 'i18n', jqueryui_available[l]), [jqueryui.jqueryui, ])
    return None


def jqueryui_i18n_need(request):
    i18n = jqueryui_i18n(request)
    if i18n is not None:
        i18n.need()
