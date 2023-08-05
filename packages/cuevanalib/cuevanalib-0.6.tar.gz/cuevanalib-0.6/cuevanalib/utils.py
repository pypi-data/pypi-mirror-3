#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import string
from unicodedata import normalize
from urlparse import urlparse
from pyquery import PyQuery


def slugify(text, delim=u'-'):
    """Generates an slightly worse ASCII-only slug."""
    _punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')
    result = []
    for word in _punct_re.split(unicode(text).lower()):
        word = normalize('NFKD', word).encode('ascii', 'ignore')
        if word:
            result.append(word)
    return unicode(delim.join(result))


def urlparams(url):
    """
    Get an URL an return a dictionary of its query params
    """
    url = urlparse(url)
    return dict([part.split('=') for part in url[4].split('&')])


def get_numbers(s):
    """Extracts all integers from a string an return them in a list"""

    return map(int, re.findall(r'[0-9]+', unicode(s)))


def smart_capwords(s):
    """
    Similar to string.capwords() but keep lowercase few common conectors
    as 'of', 'and', etc
    """
    to_keep = set(['of', 'the', ' and', 'de', 'is', 'y', 'with', 'it'])
    s = string.capwords(s)
    for word in to_keep:
        cap_word = ' ' + word.capitalize()
        if cap_word in s:
            word = 'IT' if word == 'it' else word   # special case
            s = s.replace(cap_word, ' ' + word)
    return s

def get_ids(pq):
    """given a PyQuery instance with li, return the second number for
       onclick attr"""
    return [int(PyQuery(li).attr('onclick').split('"')[1])
                            for li in pq('li')]
