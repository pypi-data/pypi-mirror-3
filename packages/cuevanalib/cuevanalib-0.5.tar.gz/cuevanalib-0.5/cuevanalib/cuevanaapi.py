#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A lib trying to work as Cuevana_ missing API

.. _Cuevana: http://www.cuevana.tv

"""

import re
import sys
import codecs
import string
import urllib
import hashlib
import cPickle as pickle

from . import __version__
from pyquery import PyQuery as pq
import utils
from downloaders import smart_urlretrieve

__author__ = "Martín Gaitán <gaitan AT gmail.com>"


URL_BASE = 'http://www.cuevana.tv'
BOX = '/box/%d.jpg'
SERIES = '/series'
MOVIES = '/peliculas'
PLAYER = "/player/source?id=%d"
RSS_MOVIES = "/rss/peliculas"
RSS_SERIES = "/rss/series"
SOURCE_GET = "/player/source_get"
SUB_EPISODE = "/download_sub?file=s/sub/%d_%s.srt"
SUB_MOVIE = "/download_sub?file=sub/%d_%s.srt"
SEARCH = "/buscar/?q=%s&cat=%s"

re_movie = re.compile(URL_BASE + MOVIES + '/[\d]+/[a-z0-9-]+/?$')
re_episode = re.compile(URL_BASE + SERIES + '/[\d]+/[a-z0-9-]+/[a-z0-9-]+/?$')
re_show = re.compile(URL_BASE + SERIES + '/[\d]+/[a-z0-9-]+/?$')

LANGS = {'Esp': 'ES', 'Spa': 'ES', 'Ing': 'EN',
         'Eng': 'EN', 'Por': 'PT'}


class CuevanaAPI(object):
    """Main class"""

    def __init__(self, show_only=None):
        """
        :param show_only: -- Limits sources links to given services. 
                             Could be a `string` or an iterable. 
        """
        self.show_only = show_only

    def get_show(self, title, return_all=False):
        """
        Retrieve a show object by its title. If any show match `title`, returns `None`

        return_all -- if it's `False` (default) returns the just most relevant show match
                      if it's `True`, returns  a list :class:`Show` sorted by relevance
        """
        p = pq(URL_BASE + SERIES)
        title = utils.smart_capwords(title)
        matchs = p('li:contains("%s")' % title)
        if not matchs:
            return None
        elif len(matchs) > 1:
            #sorting to get the most relevant in the first place
            matchs.sort(key=lambda l: l.text.index(title))
        shows = []
        for m in matchs:
            show_id = utils.get_numbers(m.attrib['onclick'])[1]
            #FIX-ME : slugify title
            url = URL_BASE + SERIES + "/%d/dummy" % show_id
            shows.append(Show(url))
        if not return_all or len(matchs) == 1:
            return shows[0]
        else:
            return shows

    def search(self, q, cat='title'):
        """
        Search content using cuevana's search engine

        q -- the query string
        cat -- type of search. Valid values are'title' (default), 
                                'episode', 'actor' or 'director'
        """
        cat_spa = {'episode': 'episodio', 'title': 'titulo',
                    'actor': 'actor', 'director': 'director'}
        
        if cat not in cat_spa.keys():
            raise NotValidSearchCategory("%s not in %s" % (cat, repr(cat_spa.keys()))) 
        cat = cat_spa[cat] 
        q = q.lower().replace(' ', '+')     #FIX ME urlencode ?
        p = pq(URL_BASE + SEARCH % (q, cat))        
        titles = [e.text for e in  p('div.tit a')]
        links = [e.values()[0] for e in  p('div.tit a')]
        if not titles:
            return None
        #TO DO: this should be a generator returning a result page
        #on each next() or has an optional param `page`        
        return [dispatch(URL_BASE + l, title=t) for t, l in zip(titles, links)]

    def _rss(self, feed):
        rss = pq(feed, parser='xml')
        titles = rss('item title').map(lambda i, e: pq(e).text()) #FIX ME
        links = rss('item link').map(lambda i, e: pq(e).text())
        return [dispatch(l, title=t) for t, l in zip(titles, links)]

    def rss_movies(self):
        """
        Returns a list of last movies published, extrated from RSS feed
        """
        return self._rss(URL_BASE + RSS_MOVIES)

    def rss_series(self):
        """
        Returns a list of last show episodes published, extrated from RSS feed
        """
        return self._rss(URL_BASE + RSS_SERIES)

    def load_pickle(self, pickled):
        """Returns and object (:class:`Movie`, :class:`Episode` or 
        :class:`Show`), from a pickled string representation with checksum
        appended.

        Use as the restore function of :meth:`Content.get_pickle` and 
        :meth:`Show.get_pickle`

        pickled -- A pickled dumps with :mod:`sha1` checksum appended
        
        :returns: :obj:`Movie`, :obj:`episode` or :obj:`Episode`
        :raises:  :exc:ValueError -- if hash not match
        """
        HASHLEN = 20   
        data, checksum = pickled[:-HASHLEN], pickled[-HASHLEN:]
        if hashlib.sha1(data).digest() != checksum:
            raise ValueError("Pickle hash does not match!")
        return pickle.loads(data)
            
    
        

class Content(object):
    """
    A movie/episode base class.
    """
    def __init__(self, url, **kwargs):
        self._url = url
        self._cid = utils.get_numbers(url)[0]
        self._sources = []
        self._populated = False

        if 'title' in kwargs:
            self._title = kwargs['title']
        if 'year' in kwargs:
            self._year = kwargs['year']

    def __unicode__(self):
        return u"<%s: %s>" % (type(self).__name__, self.title)
    
    def __repr__(self):
        return unicode(self)

    #pickling porpouses
    def __getstate__(self):
        return self.__dict__

    #unpickling porpouses
    def __setstate__(self, state):
        self.__dict__ = state

    @property
    def cid(self):
        return self._cid

    @property
    def url(self):
        return self._url

    @property
    def title(self):
        return self._title

    @property
    def cast(self):
        return self._cast

    @property
    def director(self):
        return self._director

    @property
    def script(self):
        return self._script

    @property
    def producer(self):
        return self._producer

    @property
    def gender(self):
        return self._gender

    @property
    def duration(self):
        return self._duration

    @property
    def year(self):
        return self._year

    @property
    def plot(self):
        return self._plot

    @property
    def subs(self):
        """
        A dictionary of urls to subtitles in *.srt* format
        with two letter uppercase code language as keys.

        >>> print self.subs.keys()
            ('ES', 'EN')
        """
        return self._subs

    def _get_subs(self, p):
        subs = p('div.right_uploader + div').text().split(': ')[-1]
        if subs != 'No':
            subs = [LANGS[k[:3]] for k in  subs.split(', ')]
            self._subs = dict([(lang, URL_BASE + self._sub_url % (self.cid, lang))
                                        for lang in subs])
        else:
            self._subs = {}

    @property
    def sources(self):
        """
        Return a list of links to the content
        """

        if not self._sources:
            p = pq(self._player_url)
            #import ipdb;ipdb.set_trace()
            try:
                for source in p("script:gt(2)"):
                    if 'goSource' in source.text:
                        key = source.text.split("'")[1]
                        host = source.text.split("'")[3]
                        params = urllib.urlencode({'key': key, 'host': host})
                        f = urllib.urlopen(URL_BASE + SOURCE_GET, params)  # POST
                        self._sources.append(f.read().lstrip(codecs.BOM_UTF8))
            except TypeError:
                #really. I don't understand what is happening here. 
                pass
        return self._sources

    def get_links(self):
        """
        Return sources in as a formatted string
        """
        info = self.pretty_title + '\n'
        info += '-' * len(self.pretty_title) + '\n\n'
        info += '\n'.join(self.sources) + '\n\n'
        return info

    def get_pickle(self):
        """return a pickled representation with a hash appendend"""
        s = pickle.dumps(self)
        s += hashlib.sha1(s).digest()
        return s


class Movie(Content):
    """
    Movie class.

    Should be instantiated via :func:`dispatch`
    """
    
    _sub_url = SUB_MOVIE
    
    def __init__(self, url, **kwargs):
        Content.__init__(self, url, **kwargs)
        self._player_url = (URL_BASE + PLAYER) % self.cid

    def __getattr__(self, name):
        if not self._populated:
            p = pq(self.url)
            info = p('#info table td:not(.infolabel)')

            self._title = unicode(info[0].text)
            get_info_list = lambda index: [v.strip() for v in info[index].text_content().split(',') if v.strip() != '']
            self._cast = get_info_list(1)
            self._director = get_info_list(2)
            self._script = get_info_list(3)
            self._producer = info[4].text
            self._gender = info[5].text
            self._duration = info[6].text
            self._year = int(info[7].text)
            self._plot = info[8].text
            self._get_subs(p)
            self._populated = True
        if hasattr(self, name):
            return getattr(self, name)
        else:
            raise AttributeError("object has no attribute '%s'" % name)
    
    def filename(self, format='long', extension='srt'):
        """
        return a string valid as filename to a renaming process

        `format` could be 'long' or 'short'
        """
        s = ""
        if format == 'shortness':
            # TO DO
            pass
        if format == 'short':
            s = u"{0}.{1}".format(self.title.replace(' ', ''),
                                            extension)
        elif format == 'long':
            s = u"{0.title} ({0.year}).{1}".format(self, extension)
        elif format== 'verbose':
            # TO DO
            pass
        return s

    @property
    def thumbnail(self):
        """return the url to a thumbnail of the box cover

        .. versionadded:: 0.2
        """
        return URL_BASE + BOX % self._cid

    @property
    def pretty_title(self):
        """return a the title and other info in a pretty way"""
        return "%s (%d)" % (self.title, self.year)



class Episode(Content):
    """
    Show episode class

    Should be instantiated via :func:`dispatch`
    """
    
    _sub_url = SUB_EPISODE
    
    def __init__(self, url, **kwargs):
        Content.__init__(self, url, **kwargs)
        self._player_url = (URL_BASE + PLAYER) % self.cid + '&tipo=s'

    def __getattr__(self, name):
        if not self._populated:
            # TO DO . isn't a better idea to do this with __slots__ ?
            p = pq(self.url)
            info = p('#info table td:not(.infolabel)')
            self._show = info[0].text
            self._title = unicode(info[1].text).encode('utf-8')
            get_info_list = lambda index: [v.strip() for v in info[index].text_content().split(',') if v.strip() != '']
            self._cast = get_info_list(2)
            self._director = get_info_list(3)
            self._script = get_info_list(4)
            self._producer = info[5].text
            self._gender = info[6].text
            self._year = int(info[7].text)
            self._plot = info[8].text

            self._get_subs(p)

            self._sid = utils.get_numbers(p('.headimg img').attr('src'))[0]

            #populate season/episode
            a = utils.get_numbers(p('div.right_uploader + div').text())
            self._season = a[0]
            self._episode = a[1]

            #next and previous
            close_url = lambda selector: p(selector).attr('onclick').\
                                replace("window.location='", URL_BASE )[:-1]

            self._next = close_url('.epi_sig')
            self._prev = close_url('.epi_ant')

            self._populated = True
        if hasattr(self, name):
            return getattr(self, name)
        else:
            raise AttributeError("object has no attribute '%s'" % name)



    def __unicode__(self):
        return u"<%s: S%02dE%02d>" % (type(self).__name__, self.season, 
                                                                self.episode)


    @property
    def season(self):
        """The season to which this episode belongs

        :returns: `int`  
        """
        return self._season

    @property
    def show(self):
        """Return the title of the show"""
        return self._show

    @property
    def episode(self):
        """Return the number of episode"""
        return self._episode

    @property
    def show_object(self):
        """
        return the Show() object to wich this episode belongs
        """
        url = URL_BASE + SERIES + "/%d/dummy" % self._sid
        return dispatch(url)

    @property
    def next(self):
        """Return the next episode. 
        
        If it's the last episode of the season returns the first one of 
        the next season. 
        If it's the last episode available return None
        """
        if self._next:
            return dispatch(self._next)
        else:
            show = self.show_object
            seasons = show.seasons
            if self.season + 1 <= len(seasons):
                return show.get_episode(self.season + 1, 1)
            
        
    @property
    def previous(self):
        """Return the previous episode in the season

        If it's the first episode of a season returns the last one of 
        the previous season. 
        If it's the first episode available return None
        """
        if self._prev:
            return dispatch(self._prev)
        else: 
            show = self.show_object
            seasons = show.seasons
            if self.season - 1 >= 1:
                return seasons[self.season - 2][-1]

    def filename(self, format='long', extension='srt'):
        """
        Return a formatted string valid as filename to a renaming process

        `format` could be 'long' or 'short'
        """
        s = ""
        if format == 'shortness':
            # TO DO
            pass
        elif format == 'short':
            f = (self.show.replace(' ', ''), self.season, self.episode,
                extension) 
            s = u"{0}{1:01d}x{2:02d}.{3}".format(*f)
        elif format == 'long':
            f = (self.show, self.season, self.episode, self.title, self.year,
                extension)
            s = u"{0} S{1:02d}E{2:02d} - {3} ({4}).{5}".format(*f)
        elif format == 'verbose':
            # TO DO
            pass
        return s

    @property
    def thumbnail(self):
        """return the url to a thumbnail of the box cover"""
        return URL_BASE + BOX % self._sid


    @property
    def pretty_title(self):
        """return a the title and other info in a pretty way

        .. versionadded:: 0.2
        """
        info = '%s (S%02dE%02d) - ' % (self.show, self.season, self.episode)
        info += "%s (%d)" % (self.title, self.year)
        return info

class Show(object):
    """
    Show class

    Its a container of episodes.
    """

    def __init__(self, url):
        self._url = url
        self._sid = utils.get_numbers(url)[0]
        self._seasons = []
        self._populated = False

    #pickling porpouses
    def __getstate__(self):
        return self.__dict__
 
    #unpickling porpouses
    def __setstate__(self, state):
        self.__dict__ = state

    def __getattr__(self, name):
        if not self._populated:
            p = pq(self.url)
            self._title = p('div.tit').text()
            self._plot = p('h4 + p').text().replace('\r\n', ' ')
            self._populated = True
        if hasattr(self, name):
            return getattr(self, name)
        else:
            raise AttributeError("object has no attribute '%s'" % name)

    @property
    def title(self):
        """Title of the show"""
        return self._title

    @property
    def plot(self):
        """a short sinopsys of the show plot"""
        return self._plot

    @property
    def url(self):
        """URL to this show"""
        return self._url

    @property
    def seasons(self):
        """
        A list of episode lists [[ep1x1, ...], [ep2x1..], ..]
        """
        if not self._seasons:
            p = pq(self.url)
            p.make_links_absolute(base_url=URL_BASE)

            for s in p('ul[id^=temp]'):
                episodes = [Episode(a.attrib['href']) for a in pq(s)('a')]

                self._seasons.append(episodes)

        return self._seasons

    def __unicode__(self):
        return u'<Show: %s>' % self.title

    def __repr__(self):
        return unicode(self)

    def get_season(self, season):
        """Return a list of Episodes of the given season

         Valid parameter:

            get_season('s01')
            get_season('temp1')
            get_season(1)

        .. deprecated:: 0.4
           Use :meth:`~.get_episodes` instead. 
        """
        #raise DeprecationWarning("Deprecated: use get_episodes() instead")
        season = utils.get_numbers(season)[0]

        if 0 < season <= len(self.seasons):
            return self.seasons[season - 1]
        else:
            raise UnavailableError('Unavailable season %s' % season)

    def get_episode(self, season_or_both, episode=None):
        """
        Return one specific episode.

        Valid parameter/s:

            get_episode('s01e10')
            get_episode('1x10')
            get_episode(1, 10)

        .. deprecated:: 0.4
           Use :meth:`~.get_episodes` instead. 
        """

        numbers = utils.get_numbers(season_or_both)
        season = self.get_season(numbers[0])
        if len(numbers) == 2:
            episode = numbers[1]
        if 0 < episode <= len(season):
            return season[episode - 1]
        else:
            raise UnavailableError('Unavailable episode')

    def get_episodes(self, start, end=''):
        """
        Return a list between both limits including them
        Example 's01e10' - 's02e11' 
         
        If start has just one number, first episode is asummed
        If end has just number, last episode is asummed

        .. versionadded:: 0.4
        """
        episodes = []

        numbers_start = utils.get_numbers(start)
        numbers_end = numbers_start[:] if end == '' else utils.get_numbers(end) 

        if not (len(numbers_start) >= 1 and len(numbers_end) >= 1):
            raise UnavailableError("can't decode slice")
        if numbers_start[0] > numbers_end[0]:
            raise UnavailableError('start season greater than end season')
        if numbers_start[0] <= 0:
            raise UnavailableError('Unavailable start season')
        if numbers_end[0] > len(self.seasons):
            raise UnavailableError('Unavailable end season')
    

        season_s = self.get_season(numbers_start[0])
        if len(numbers_start) == 2:
            episode_s = numbers_start[1]
            if episode_s < 1  or  episode_s > len(season_s):
                raise UnavailableError('Unavailable start episode')
        else:
            episode_s = False

        season_e = self.get_season(numbers_end[0])
        if len(numbers_end) == 2:
            episode_e = numbers_end[1]
            if episode_e < 1  or  episode_e > len(season_e):
                raise UnavailableError('Unavailable end episode')
        else:
            episode_e = False

        for season in range(numbers_start[0], numbers_end[0] + 1):
            episodes.extend(self.seasons[season - 1])
        
        if episode_s:
            episodes = episodes[episode_s - 1:]
        if episode_e:
            end = len(season_e) - episode_e
            episodes = episodes[:len(episodes)-end]
        
        return episodes
            
    def get_pickle(self):
        """return a pickled representation with a hash appendend"""
        s = pickle.dumps(self)
        s += hashlib.sha1(s).digest()
        return s


#Exceptions
class UnavailableError(Exception):
    pass

class NotValidURL(ValueError):
    pass

class NotValidSearchCategory(KeyError):
    pass


def dispatch(url, **kwargs):
    """
    A dispatcher function that return the right object
    based on its URL

    Optional keyword arguments: `title` and/or `year` 
    """
    if re.match(re_movie, url):
        return Movie(url, **kwargs)
    elif re.match(re_episode, url):
        return Episode(url, **kwargs)
    elif re.match(re_show, url):
        return Show(url)
    else:
        raise NotValidURL('This is not a valid content URL')
