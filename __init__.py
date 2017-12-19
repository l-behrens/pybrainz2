#!/usr/bin/python

from requests import get as _get
from requests import post as _post
from requests.exceptions import RequestException
from json import loads as _loads
import urllib as _urllib
import json as _json
import logging as _logging


'''
Since this is just a wrapper I liked the idea of gathering
all possible options in a dict (syntax). If you want to know
which arguments the member methods **kwargs take, here they are =)

You can find exhaustive information to the options specified below
in the musicbrainz API doc:
https://musicbrainz.org/doc/Development/XML_Web_Service/Version_2/Search

'''

syntax = {
    'artist': [
        'alias', 'area', 'arid',  'artist', 'artistaccent', 'begin', 'beginarea',
        'comment', 'country', 'end', 'endarea', 'ended', 'gender', 'ipi',
        'sortname', 'tag', 'type'],
    'area': [
        'aid', 'alias', 'area', 'begin', 'comment', 'end', 'ended', 'iso',
        'iso1', 'iso2', 'iso3', 'sortname', 'type'],
    'cdstub': [
        'artist', 'barcode', 'comment', 'discid', 'title', 'tracks'],
    'label': [
        'alias', 'area', 'begin', 'code', 'comment', 'country',
        'end', 'ended', 'ipi', 'label', 'labelaccent', 'laid',
        'sortname', 'type', 'tag'],
    'recording': [
        'arid', 'artist', 'artistname', 'creditname', 'comment', 'country',
        'date', 'dur', 'format', 'isrc', 'number', 'position', 'primarytype',
        'qdur', 'recording', 'recordingaccent', 'reid', 'release', 'rgid',
        'rid', 'secondarytype', 'status', 'tid', 'tnum', 'tracks', 'tracksrelease',
        'tag', 'type', 'video'],
    'release-group': [
        'arid', 'artist', 'artistname', 'comment', 'creditname', 'primarytype', 'rgid',
        'releasegroup', 'releasegroupaccent', 'releases', 'release', 'reid',
        'secondarytype', 'status', 'tag', 'type'],
    'release': [
        'arid', 'artist', 'artistname', 'comment', 'creditname', 'primarytype',
        'rgid', 'releasegroup', 'releasegroupaccent', 'releases', 'release',
        'reid', 'secondarytyp', 'status', 'tag', 'type'],
    'tag': [
        'tag'],
    'work': [
        'alias', 'arid', 'artist', 'comment', 'iswc', 'lang', 'tag', 'type',
        'wid', 'work', 'workaccent']
}


class MusicBrainzException(Exception):
    pass


class MusicBrainzApi(object):
    '''
    async api wrapper for musicBrainz Project
    Original API Options were retrived directly from
    musicbrainz documentation. They are defined in the
    syntax dict above. All categories are available as
    member functions. e.g data from category 'artist'
    can be accessed via get_artist method. Further options
    are provided as **kwargs. The query argements take plain
    text as input
    '''

    LOG_FORMAT = "%(levelname)s %(asctime)s - %(message)s"
    API_URL = 'http://musicbrainz.org/ws/2/'
    FMT_JSON = 'json'
    FMT_XML = 'xml'

    def __init__(self, fmt=FMT_JSON, loglvl=_logging.INFO):
        ''' json = api output in json. Otherwise xml'''

        self._fmt = '&fmt=%s' % fmt

        _logging.basicConfig(
            level=loglvl,
            format=self.LOG_FORMAT)

        self.logger = _logging.getLogger('metafruits')

    # TODO: In query control characters must be escaped before sending
    async def __call__(self, category, query='', fmt=FMT_JSON, kwargs={}):
        '''set up and send the http call '''

        payload = {}
        # Flaten option dict into string
        opts = '%20'.join(['%s:%s' % (e, kwargs[e]) for e in kwargs])

        self._sanity_check(category, kwargs)

        payload['url'] = '%s%s/?query=%s%s%s' % (
            self.API_URL, category, query, opts, self._fmt)
        ret = _get(**payload)

        self.logger.debug('%s will be called' % ret.url)

        return await self._handleReturned(ret.text)

    async def _sanity_check(self, category, kwargs):
        '''check if category and keywords are accepted by the api'''
        if not category in syntax.keys():
            self.logger.error(
                'only these categories are permitted: \n%s' % syntax.keys())
            raise(MusicBrainzException(
                'category: %s not permitted by api' % category))

        for kw in kwargs:
            if(not kw in syntax[category]):
                self.logger.error(
                    'only these keywords are permitted: \n%s' % syntax[category])
                raise(MusicBrainzException(
                    'keyword: %s not permitted by api' % kw))

    async def _handleReturned(self, data):
        ''' Handles returned data from musicbrainz
        data must be valid json'''

        try:
            out = _loads(data)
        except Exception as e:
            self.logger.error('in func: %s \nException: %s' % (__name__, e))
            raise
        else:
            if 'error' in out:
                err = RequestException('MusicbrainzError %s' % (out['error']))
                self.logger.error('in func: %s \nException: %s' %
                                  (__name__, err))
            return out

        return None

    # TODO find a link to verify availability of musicbrainz'
    @property
    def is_alive(self):
        url = 'http://musicbrainz.org/ws/2/area'
        #ret = _urllib.request.urlopen(url).getcode()
        if ret == 200:
            return False
        return True

    async def get_artist(self, query='', **kwargs):
        '''
        Get an Artist Information. Following Parameters are Possible:
        alias          an alias attached to the artist
        area           the artist's main associated area
        arid           the artist's MBID
        artist         the artist's name (without accented characters)
        artistaccent   the artist's name (with accented characters)
        begin          the artist's begin date
        beginarea      the artist's begin area
        comment        the artist's disambiguation comment
        country        the 2-letter code (ISO 3166-1 alpha-2) for the artist's main associated country, or “unknown”
        end            the artist's end date
        endarea        the artist's end area
        ended          a flag indicating whether or not the artist has ended
        gender         the artist's gender (“male”, “female”, or “other”)
        ipi            an IPI code associated with the artist
        sortname       the artist's sort name
        tag            a tag attached to the artist
        type           the artist's type (“person”, “group”, ...)
        '''

        return await self.__call__('artist', query, kwargs=kwargs)

    async def get_label(self, query='', **kwargs):
        '''
        alias          the aliases/misspellings for this label
        area           label area
        begin          label founding date
        code           label code (only the figures part, i.e. without "LC")
        comment        label comment to differentiate similar labels
        country        The two letter country code of the label country
        end            label dissolution date
        ended          true if know ended even if do not know end date
        ipi            ipi
        label          label name
        labelaccent    name of the label with any accent characters retained
        laid           MBID of the label
        sortname       label sortname
        type           label type
        tag            folksonomy tag
        '''

        return await self.__call__('label', query, kwargs=kwargs)

    async def get_release(self, query='', **kwargs):
        '''
        arid                    MBID of the release group’s artist
        artist                  release group artist as it appears on the cover (Artist Credit)
        artistname              “real name” of any artist that is included in the release
                                group’s artist credit
        comment                 release group comment to differentiate similar release groups
        creditname              name of any artist in multi-artist credits, as it appears on the cover.
        primarytype             primary type of the release group (album, single, ep, other)
        rgid                    MBID of the release group
        releasegroup            name of the release group
        releasegroupaccent	name of the releasegroup with any accent characters retained
        releases                number of releases in this release group
        release                 name of a release that appears in the release group
        reid                    MBID of a release that appears in the release group
        secondarytype           secondary type of the release group (audiobook,
                                compilation, interview, live, remix soundtrack, spokenword)
        status                  status of a release that appears within the release group
        tag                     tag that appears on the release group
        type                    type of the release group, old type
                                mapping for when we did not have
                                separate primary and secondary types
        '''
        return await self.__call__('release', query, kwargs=kwargs)

    async def get_recording(self, query='', **kwargs):
        '''
        arid                    artist id
        artist                  artist name is name(s) as it appears on the recording
        artistname              an artist on the recording, each artist added as a separate field
        creditname              name credit on the recording, each artist added as a separate field
        comment                 recording disambiguation comment
        country                 recording release country
        date                    recording release date
        dur                     duration of track in milliseconds
        format                  recording release format
        isrc                    ISRC of recording
        number                  free text track number
        position                the medium that the recording should be found on, first 
                                medium is position 1
        primarytype             primary type of the release group (album, single, ep, other)
        qdur                    quantized duration (duration / 2000)
        recording               name of recording or a track associated with the recording
        recordingaccent         name of the recording with any accent characters retained
        reid                    release id
        release                 release name
        rgid                    release group id
        rid                     recording id
        secondarytype           secondary type of the release group (audiobook, 
                                compilation, interview, live, remix soundtrack, spokenword)
        status                  Release status (official, promotion, Bootleg, Pseudo-Release)
        tid                     track id
        tnum                    track number on medium
        tracks                  number of tracks in the medium on release
        tracksrelease           number of tracks on release as a whole
        tag                     folksonomy tag
        type                    type of the release group, old type mapping for when 
                                       we did not have separate primary and secondary types or
                                       use standalone for standalone recordings
        video                   true to only show video tracks
        '''
        return await self.__call__('release', query, kwargs=kwargs)
