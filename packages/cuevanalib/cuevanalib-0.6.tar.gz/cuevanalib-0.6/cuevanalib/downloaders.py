#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: Martín Gaitán <gaitan AT gmail DOT com>
# Licence: GPL v3.0

import os
import sys
import time
import urllib2
import shutil
import cookielib

from pyquery import PyQuery as pq

from progressbar_widgets import *

def megaupload(url, filename, callback=None,
                ETA2callback="auto", kbps=96, max_rate=None):
    """
    Given a megaupload URL gets the file

    Reproduce this :program:`wget` command::

       $ wget --save-cookies="mu" --load-cookies="mu" \
            -w 45 PUBLIC_MEGAUPLOAD_URL FILE_DIRECT_URL

    Arguments:
    url -- the URL to a megaupload content
    callback -- function to callback. It's useful to do something
                with the partially downloaded file. (i.e. play it)

    ETA2callback -- is the :abbr:`ETA (Estimated time to Arrival)` to
                    make the callback. Should be an :type:`int` (seconds).
                    The special value ``auto`` indicates that
                    the parameter will be estimated as ``file_size / kbps``

    kbps -- Kilobytes per seconds. It's a compression level factor. Needed if
            ``'auto'`` is given as ETA2callback
            A greater value means wait more before make the callback.
            ``95`` is a standard compression in cuevana.tv

    max_rate -- Max transfer rate in Kilobytes per seconds
                If None, no limit is apply.
    """

    if not url.startswith('http://www.megaupload.com/?d='):
        raise NotValidMegauploadLink

    cj = cookielib.CookieJar()
    opener = urllib2.build_opener( urllib2.HTTPCookieProcessor(cj) )

    p = pq(url=url, opener=lambda url: opener.open(url).read())
    url_file = p('a.down_butt1').attr('href')

    if not url_file:
        raise NotAvailableMegauploadContent

    msg = 'Downloading %s...' #if not callback else 'Buffering %s...'
    countdown(45,  msg % filename)
    try:
        response = opener.open(url_file)
        size = int(response.info().values()[0])
    except urllib2.HTTPError:
        print "Problem downloading...  :("
        return

    chunk = 4096
    if ETA2callback == "auto":
        ETA2callback = size / (kbps * 1024)
    my_eta = ETA_callback(ETA2callback, callback)

    widgets = ['', Percentage(), ' ', Bar('='),
               ' ', my_eta, ' ',
               LimitedFileTransferSpeed(max_rate=max_rate)]
    pbar = ProgressBar(widgets=widgets, maxval=size).start()
    with open(filename, 'wb') as localfile:
        copy_callback(response.fp, localfile, size, chunk,
                        lambda pos: pbar.update(pos),
                        lambda : pbar.finish())


def smart_urlretrieve(url, local, referer=''):
    """
    Analogous to urllib.urlretrieve,
    but could handle a referer and cookies.

    Use this if you want get subtitles.

    .. versionadded:: 0.4.3
    """
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener( urllib2.HTTPCookieProcessor(cj) )
    request = urllib2.Request(url)
    if referer:
        dummy = opener.open(referer).read()
        request.add_header('Referer', referer)
    response = opener.open(request)
    with open(local, 'wb') as localfile:
        shutil.copyfileobj(response.fp, localfile)



def countdown(seconds, msg="Done"):
    """
    Wait `seconds` counting down.  When it's done print `msg`
    """
    for i in range(seconds, 0, -1):
        sys.stdout.write("%02d" % i)
        time.sleep(1)
        sys.stdout.write("\b\b")
        sys.stdout.flush()
    sys.stdout.write(msg + "\n")
    sys.stdout.flush()



def copy_callback(src, dest, src_size=None, chunk=10240,
                    callback_update=None, callback_end=None):
    """
    Copy a file calling back a function on each chunk and when finish
    """
    if not src_size:
        src_size = os.stat(src.name).st_size

    cursor = 0
    while True:
        buffer = src.read(chunk)
        if buffer:
            # ..if not, write the block and continue
            dest.write(buffer)
            if callback_update:
                callback_update(cursor)
            cursor += chunk
        else:
            break

    if callback_end:
        callback_end()

    src.close()
    dest.close()

    # Check output file is same size as input one!
    dest_size = os.stat(dest.name).st_size
    if dest_size != src_size:
        raise IOError(
            "New file-size does not match original (src: %s, dest: %s)" % (
            src_size, dest_size)
        )


class NotValidMegauploadLink(Exception):
    """This is not a valid MEGAUPLOAD link"""
    pass

class NotAvailableMegauploadContent(Exception):
    """The content for the link you provided isn't available"""
    pass
