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


from functools import wraps
import errors



def restrict_access(login=None):
	"""Restrict function access unless the user has the necessary permissions.

	Raises the LoginRequired exception when appropriate.
	"""

	def wrap(function):
		@wraps(function)
		def wrapped(cls, *args, **kwargs):
			obj = getattr(cls, 'lex_session', cls)
			
			if login and not obj.is_logged_in():
				raise errors.LoginRequired(function.__name__)

		return wrapped
	return wrap