# fookebox, http://fookebox.googlecode.com/
#
# Copyright (C) 2007-2011 Stefan Ott. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import cgi
import logging

from paste.urlparser import PkgResourcesParser
from pylons import request
from pylons.controllers.util import forward
from pylons.middleware import error_document_template
from webhelpers.html.builder import literal

from fookebox.lib.base import BaseController

log = logging.getLogger(__name__)

class ErrorController(BaseController):

	"""Generates error documents as and when they are required.

	The ErrorDocuments middleware forwards to ErrorController when error
	related status codes are returned from the application.

	This behaviour can be altered by changing the parameters to the
	ErrorDocuments middleware in your config/middleware.py file.

	"""

	def document(self):
		"""Render the error document"""
		resp = request.environ.get('pylons.original_response')
		content = literal(resp.body) or cgi.escape(request.GET.get(
			'message', ''))

		accept = request.headers.get('accept')
		error = request.environ.get('pylons.controller.exception')

		if accept == 'application/json' and error:
			content = error.detail
		elif accept == 'application/json':
			content = "ERROR"

		page = error_document_template % \
			dict(prefix=request.environ.get('SCRIPT_NAME', ''),
				code=cgi.escape(request.GET.get('code',
				str(resp.status_int))), message=content)
		return page

	def img(self, id):
		"""Serve Pylons' stock images"""
		return self._serve_file('/'.join(['media/img', id]))

	def style(self, id):
		"""Serve Pylons' stock stylesheets"""
		return self._serve_file('/'.join(['media/style', id]))

	def _serve_file(self, path):
		"""Call Paste's FileApp (a WSGI application) to serve the file
		at the specified path
		"""
		request.environ['PATH_INFO'] = '/%s' % path
		return forward(PkgResourcesParser('pylons', 'pylons'))
