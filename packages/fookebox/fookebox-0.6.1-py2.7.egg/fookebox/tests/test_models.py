import unittest
from fookebox.model.jukebox import *

class FakeMPD(object):
	def __init__(self):
		self.db = []
		self.fillDB()
		self.stop()
		self.queue = []
		self._pos = 0

	def fillDB(self):
		self.db.append({
			'file': '/tmp/dummy1.mp3',
			'time': '120',
			'album': 'Fake Album 1',
			'title': 'Fake Title 1',
			'track': '1',
			'genre': 'Fake Genre 1',
			'artist': 'Fake Artist 1',
			'date': '2005',
		})
		self.db.append({
			'file': '/tmp/dummy2.sid',
			'artist': 'Fake Artist 2',
			'title': 'Fake Title 2',
		})
		self.db.append({
			'file': '/tmp/dummy3.mp3',
			'time': '144',
			'album': 'Fake Album 1',
			'title': 'Fake Title 2',
			'track': '2/4',
			'genre': 'Fake Genre 1',
			'artist': 'Fake Artist 1',
			'date': '2005',
		})
		self.db.append({
			'file': '/tmp/dummy4.ogg',
			'time': '123',
			'album': 'Fake Album 2',
			'title': 'Fake Title 3',
			'track': ['11', '12'],
			'genre': 'Fake Genre 1',
			'artist': 'Fake Artist 1',
			'date': '2005',
		})

	def stop(self):
		#self._song = None
		self._status = {
			'playlistlength': '0',
			'playlist': '5',
			'state': 'stop',
			'volume': '100',
		}

	def play(self):
		if not self.queue[0] == None:
			self._status = {
				'playlistlength': '1',
				'playlist': '5',
				'state': 'play',
				'volume': '100',
			}

			song = self.queue[self._pos]
			if 'time' in song:
				self._status['time'] = '0:%s' % song['time']
			else:
				self._status['time'] = '0:0'

	def status(self):
		return self._status

	def playDummy(self, index):
		self.queue = [self.db[index]]
		self._pos = 0
		self.play()

	def close(self):
		pass

	def disconnect(self):
		pass

	def skipTime(self, interval):
		(time, total) = self._status['time'].split(':')
		time = int(time)
		time = min(time + interval, int(total))
		self._status['time'] = "%s:%s" % (time, total)

	def add(self, file):
		for song in self.db:
			if song['file'] == file:
				self.queue.append(song)

	def delete(self, index):
		self.queue.remove(self.queue[index])
		if self._pos > index:
			self._pos -= 1

		if len(self.queue) < 1:
			self.stop()

	def playlistinfo(self):
		return self.queue

	def currentsong(self):
		song = self.queue[self._pos]

		if song != None:
			song['pos'] = self._pos

		return song

	def next(self):
		self._pos += 1

	def search(self, field, value):
		result = []

		for song in self.db:
			if field in song and song[field] == value:
				result.append(song)

		return result

class TestJukebox(unittest.TestCase):

	def setUp(self):
		self.mpd = FakeMPD()
		self.jukebox = Jukebox(self.mpd)

	def test_timeLeft(self):
		assert self.jukebox.timeLeft() == 0

		self.mpd.playDummy(0)
		self.mpd.skipTime(30)
		assert self.jukebox.timeLeft() == 90

		self.mpd.playDummy(1)
		assert self.jukebox.timeLeft() == 0

		self.mpd.skipTime(30)
		assert self.jukebox.timeLeft() == 0

	def test_queue(self):
		assert self.jukebox.isPlaying() == False

		self.jukebox.queue(self.mpd.db[0]['file'])
		assert len(self.jukebox.getPlaylist()) == 1
		assert self.jukebox.isPlaying() == True

		self.jukebox.queue(self.mpd.db[1]['file'])
		assert len(self.jukebox.getPlaylist()) == 2
		assert self.jukebox.isPlaying() == True

	def test_cleanQueue(self):
		self.jukebox.queue(self.mpd.db[0]['file'])
		self.jukebox.queue(self.mpd.db[1]['file'])
		assert self.jukebox.getCurrentSong()['title'] == 'Fake Title 1'

		self.jukebox.next()
		assert self.jukebox.getCurrentSong()['title'] == 'Fake Title 2'
		assert len(self.jukebox.getPlaylist()) == 2

		self.jukebox.cleanQueue()
		assert self.jukebox.getCurrentSong()['title'] == 'Fake Title 2'
		assert len(self.jukebox.getPlaylist()) == 1

	def test_searchArtist(self):
		albums = self.jukebox.search('artist', 'Fake Artist 1')
		assert len(albums) == 2
		assert len(albums['Fake Album 1'].tracks) == 2
		assert len(albums['Fake Album 2'].tracks) == 1

class TestTrack(unittest.TestCase):

	def setUp(self):
		self.mpd = FakeMPD()

	def test_trackNum(self):
		track = Track()
		track.load(self.mpd.db[0])
		assert track.track == 1

		track = Track()
		track.load(self.mpd.db[2])
		assert track.track == 2

		track = Track()
		track.load(self.mpd.db[3])
		assert track.track == 11
