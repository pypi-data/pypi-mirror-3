import re
import urllib
import tornado.web
import tornado.gen
import tornado.httpclient

from xml.etree import ElementTree as etree



'''Example:

xiamiclient = AsyncXiamiClient()

@route('/xiaoyu/')
class XiaoyuHandler(RequestHandler):

    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        url = self.get_argument('url', None)
        if url:
            m = re.match(r'http://www.xiami.com/song/(\d+)', url)
            if m:
                sid = m.group(1)
                tracklist, error = yield xiamiclient.getSong(sid)
                self.render('frontend/xiami.html', url=url, tracklist=tracklist, playlist=None)
                return

            m = re.match(r'http://www.xiami.com/album/(\d+)', url)
            if m:
                aid = m.group(1)
                playlist, error = yield xiamiclient.getAlbum(aid)
                self.render('frontend/xiami.html', url=url, tracklist=None, playlist=playlist)
                return

        self.render('frontend/xiami.html', url='', tracklist=None, playlist=playlist)

'''


class AsyncXiamiClient(object):

    def getAlbum(self, album_id):
        url = 'http://www.xiami.com/song/playlist/id/%s/type/1' % album_id

        def _task(callback):
            def _callback(response):
                if response.error:
                    res = (None, 'network error')
                else:
                    songs = self.parsePlaylist(response.body)
                    res = (songs, None)
                callback(res)
            http_client = tornado.httpclient.AsyncHTTPClient()
            http_client.fetch(url, _callback)

        return tornado.gen.Task(_task)

    def getSong(self, song_id):
        url = 'http://www.xiami.com/widget/xml-single/sid/' + song_id

        def _task(callback):
            def _callback(response):
                if response.error:
                    res = (None, 'network error')
                else:
                    songs = self.parseTrackList(response.body)
                    res = (songs, None)
                callback(res)
            http_client = tornado.httpclient.AsyncHTTPClient()
            http_client.fetch(url, _callback)

        return tornado.gen.Task(_task)

    def parseTrackList(self, text):
        xml = etree.fromstring(text)
        xtracks = xml.findall('track')
        songs = map(Song, xtracks)
        for song in songs:
            song.location = getLocation(song.location)
        return songs

    def parsePlaylist(self, text):
        text = text.replace(' xmlns="http://xspf.org/ns/0/"', '')
        xml = etree.fromstring(text)
        xtracks = xml.findall('trackList/track')
        songs = map(Song, xtracks)
        for song in songs:
            song.location = getLocation(song.location)
        return songs


class Song(object):

    PROPERTIES = ['title', 'song_id', 'album_id', 'album_name',
                  'object_name', 'insert_type', 'background',
                  'grade', 'artist', 'location', 'ms', 'lyric', 'pic']

    def __init__(self, xml):
        for n in list(xml):
            setattr(self, n.tag, n.text)
        self.xml = xml

    def __repr__(self):
        return 'Song:' + str(dict([(n.tag, getattr(self, n.tag)) for n in list(self.xml)]))


def getSongs(*songids):
    url = 'http://www.xiami.com/song/playlist/id/%s/object_name/default/object_id/0/cat_id/0'
    url = url % ','.join(songids)
    o = urllib.urlopen(url)
    text = o.read()
    text = text.replace(' xmlns="http://xspf.org/ns/0/"', '')
    xml = etree.fromstring(text)
    xtracks = xml.findall('trackList/track')
    songs = map(Song, xtracks)
    for song in songs:
        song.location = getLocation(song.location)
    return songs


def getSong(songid):
    url = 'http://www.xiami.com/widget/xml-single/sid/' + songid
    o = urllib.urlopen(url)
    text = o.read()
    xml = etree.fromstring(text)
    xlocation = xml.find('track/location')
    raw = xlocation.text
    return getLocation(raw)


def getLocation(_arg1):
    _local2 = int(_arg1[0])
    _local3 = _arg1[1:]
    _local4 = len(_local3) / _local2
    _local5 = (len(_local3) % _local2)
    _local6 = [''] * _local2
    _local7 = 0;
    while _local7 < _local5:
        if not _local6[_local7]:
            _local6[_local7] = "";
        i = int((_local4 + 1) * _local7)
        _local6[_local7] = _local3[i: i+(_local4 + 1)]
        _local7 += 1

    _local7 = _local5
    while _local7 < _local2:
        i = int((_local4 * (_local7 - _local5)) + ((_local4 + 1) * _local5))
        _local6[_local7] = _local3[i: i+_local4]
        _local7+=1;
    _local8 = "";
    _local7 = 0;
    while _local7 < len(_local6[0]):
        _local10 = 0;
        while _local10 < len(_local6):
            _local8 = (_local8 + _local6[_local10][_local7:_local7+1])
            _local10+=1;
        _local7+=1;
    _local8 = urllib.unquote(_local8)
    _local9 = "";
    _local7 = 0;
    while _local7 < len(_local8):
        if _local8[_local7] == "^":
            _local9 = (_local9 + "0");
        else:
            _local9 = (_local9 + _local8[_local7]);
        _local7+=1;
    _local9 = _local9.replace("+", " ");
    return (_local9);


if __name__ == '__main__':
    print getSong('1770386148')
    print getSongs('1770386148', '1770813865')


