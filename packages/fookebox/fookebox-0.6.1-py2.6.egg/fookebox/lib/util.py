# fookebox, http://fookebox.googlecode.com/
#
# copyright (c) 2007-2011 stefan ott. all rights reserved.
#
# this program is free software: you can redistribute it and/or modify
# it under the terms of the gnu general public license as published by
# the free software foundation, either version 3 of the license, or
# (at your option) any later version.
#
# this program is distributed in the hope that it will be useful,
# but without any warranty; without even the implied warranty of
# merchantability or fitness for a particular purpose.  see the
# gnu general public license for more details.
#
# you should have received a copy of the gnu general public license
# along with this program.  if not, see <http://www.gnu.org/licenses/>.

import os

class FileSystem(object):
	@staticmethod
	def exists(path):
		return os.path.exists(path.encode('utf8'))

	@staticmethod
	def isdir(path):
		return os.path.isdir(path.encode('utf8'))

	@staticmethod
	def listdir(path):
		return os.listdir(path.encode('utf8'))
