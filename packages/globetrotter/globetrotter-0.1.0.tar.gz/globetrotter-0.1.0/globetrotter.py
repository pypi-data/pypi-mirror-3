# -*- coding: utf-8 -*-
#
#  globetrotter.py
#  globetrotter
#

"""
Approximate country and language finding for pycountry.
"""

import pycountry

def find_country(name):
    "Find a country's information given an approximate name."
    norm_name = _norm_countries[_norm_string(name)]
    c = pycountry.countries.get(name=norm_name)
    if not c:
        raise KeyError(name)
    return c

def find_language(name):
    "Find a language's information given an approximate name."
    norm_query = _norm_string(name)
    norm_name = _norm_languages.get(norm_query)
    if norm_name:
        l = pycountry.languages.get(name=norm_name)
        assert l
        return l

    # try prefix matching
    matches = [l for (n, l) in _norm_languages.iteritems() if
            n.startswith(norm_query)]
    if matches and len(matches) == 1:
        return pycountry.languages.get(name=matches[0])

    raise KeyError(name)

def _norm_string(s):
    return s.replace(' ', '').lower()

_norm_countries = {_norm_string(c.name): c.name
        for c in pycountry.countries.objects}

_norm_languages = {_norm_string(l.name): l.name
        for l in pycountry.languages.objects}

