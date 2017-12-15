#!/usr/bin/python

import unittest
import time
import asyncio

from pprint import pprint
from musicbrainz2 import MusicBrainzApi


class MusicBrainzApiTest(unittest.TestCase):
    '''
    TODO: 
    '''

    def setUp(self):
        self.brainz = MusicBrainzApi()
        self.loop = asyncio.get_event_loop()

    def async_executor(self, f):
       # gathering =  asyncio.ensure_future(asyncio.gather(f))
       # time.sleep(2)
       # return  gathering.result()
        return self.loop.run_until_complete(asyncio.gather(f))

    def test_artist_search(self):
        options = ['alias', 'area', 'arid',  'artist', 'artistaccent', 'begin', 'beginarea',
                   'comment', 'country', 'end', 'endarea', 'ended', 'gender', 'ipi',
                   'sortname', 'tag', 'type']

        kwargs = {o: 'test' for o in options}

        ret = self.async_executor(self.brainz.get_artist(**kwargs))
        self.assertTrue(ret, 'return dict must not be empty')

        arid = '30e29226-c603-486e-8a45-1d057ba7feaf'
        ret = self.brainz.get_artist(arid=arid)
        self.assertTrue(ret, 'return dict must not be empty')


if __name__ == "__main__":
    unittest.main()
