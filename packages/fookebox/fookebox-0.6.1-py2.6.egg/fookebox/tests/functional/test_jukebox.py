from fookebox.tests import *

class TestJukeboxController(TestController):

	def test_status(self):
		response = self.app.get(
			url(controller='jukebox', action='status'))
		# Test response...
