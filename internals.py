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


from requests import Request
from requests.compat import urljoin

def _prepare_request(lex_session, url, params, data, auth, files):
	"""Return a requests Request object that can be "prepared"."""

	headers = {}
	headers.update(lex_session.http.headers)

	request = Request(method='GET', url=url, headers=headers, params=params, auth=auth, cookies=lex_session.http.cookies)

	if not data and not files: # GET request
		return request
	if not auth:
		data.setdefault('api_type', 'json')
	request.method = 'POST'
	request.data = data
	request.files = files
	return request
	
def _get_sorter(order=''):
	"""Return a function to generate specific plugin listings."""
	if order == '':
		order = 'recent'

	def _sorted(self, *args, **kwargs):
		if not kwargs.get('params'):
			kwargs['params'] = {}
		for key, value in self._params.iteritems():
			kwargs['params'].setdefault(key, value)

		kwargs['params'].setdefault('order_by', order)

		url = self._url
		return self.lex_session.get_content(url, *args, **kwargs)
	return _sorted

def _get_user_plugins(user_id='', query='downloaded'):
	"""Return function to generate a list of a User's plugins."""
	def _plugins(self, order='', *args, **kwargs):
		"""Return a get_content generator for some LEXContentObject type."""
		if not user_id:
			user_id = self.user.id
		if query == 'uploaded':
			kwargs.setdefault('params', {})
			kwargs['params'].setdefault('creator', user_id)
