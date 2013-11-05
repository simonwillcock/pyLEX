# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


class ClientException(Exception):

	"""Base exception class for errors that don't involve the remote API."""

	def __init__(self, message):
		super(ClientException, self).__init__()
		self.message = message

	def __str__(self):
		return self.message


class LoginRequred(ClientException):

	"""Indicates that a logged in session is required."""

	def __init__(self, function, message=None):
		if not message:
			message = '`{0}` requires a logged in session'.format(function)
		super(LoginRequred, self).__init__(message)


class APIExcpetion(Exception):

	"""Base exception class for the LEX API error message exceptions."""

	def __init__(self, error_type, message, field='',  response=None):
		super(APIExcpetion, self).__init__()
		self.error_type = error_type
		self.message = message
		self.field = field
		self.response = response

	def __str__(self):
		if hasattr(self, 'ERROR_TYPE'):
			return '`%s` on field `%s`' % (self.message, self.field)
		else:
			return '(%s) `%s` on field `%s`' % (self.error_type, self.message, self.field)
