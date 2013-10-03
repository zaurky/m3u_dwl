#!/usr/bin/python
"""
M3u downloader module
"""

import atexit
import os
import sys
import time
import urllib2
from urllib2 import HTTPError


class NoPlayList(Exception):
    """ No playlist where found """
    def __repr__(self):
        print "No playlist found"


class M3uDwl(object):
    """ M3u downloader object """
    pl1_url = None
    pl2_url = None
    http_dir = None
    fhandle = None

    def __init__(self, m3u_url, filename):
        self.pl1_url = m3u_url
        self.filename = filename

        self.last_seq = None
        self.last_url = []
        self.size = 0

        atexit.register(self.exit)
        print "Will download %s into %s" % (self.pl1_url, self.filename)

    @staticmethod
    def parse_m3u(data):
        """ parse a simple m3u file into a dict """
        m3u = {}

        for line in data.split('\n'):
            if not line:
                continue

            if '#EXTINF' in line:
                m3u.setdefault('#EXTINF', []).append(line.split(':')[1])
            elif ':' in line:
                m3u.update(dict([line.split(':')]))
            elif line.startswith('#'):
                continue
            else:
                m3u.setdefault('data', []).append(line)

        return m3u

    @classmethod
    def get_playlist(cls, url):
        """ get the content at url and parse it to get the m3u dict """
        playlist = None
        try:
            playlist = cls.parse_m3u(urllib2.urlopen(url).read())
        except HTTPError:
            pass

        if not playlist:
            raise NoPlayList()

        return playlist

    def get_second_playlist(self):
        """ in the actuel test case, there is two levels of m3u to get data """
        pl1 = self.get_playlist(self.pl1_url)
        self.pl2_url = os.path.join(self.http_dir, pl1['data'][0])

    def next_seq(self, seq):
        """ return True if the seq is the next number """
        return self.last_seq is None or self.last_seq != seq

    def get_chunk(self):
        """ download the chunks from pl2_url m3u file """
        pl2 = self.get_playlist(self.pl2_url)

        # get the seq, and loop if pl2_url is no longer ok
        if not '#EXT-X-MEDIA-SEQUENCE' in pl2:
            self.get_second_playlist()
            return

        seq = pl2['#EXT-X-MEDIA-SEQUENCE']

        if not self.next_seq(seq):
            return

        for data_name in pl2['data']:
            # check that we are not getting the same data chunk
            if data_name in self.last_url:
                return

            # get data into file
            data_url = os.path.join(self.http_dir, data_name)
            data = urllib2.urlopen(data_url).read()
            self.fhandle.write(data)
            self.size += len(data)

        self.last_seq = seq
        self.last_url = pl2['data']

    def run(self):
        """ loop as long as there is data and download it """
        self.fhandle = open(self.filename, 'w', 0)
        self.fhandle.write("\x00\x00\xba\x01\x00\x21\x00\x01")

        self.http_dir = os.path.dirname(self.pl1_url)

        self.get_second_playlist()

        while True:
            self.get_chunk()
            time.sleep(1)

    def exit(self):
        """ when the class is deleted """
        print "got %d bits" % self.size
        self.fhandle.close()
