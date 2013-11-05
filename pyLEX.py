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


import requests
import cookielib
import json
from requests.compat import urljoin
from handlers import DefaultHandler
from internals import _prepare_request
import objects
import decorators
from BeautifulSoup import BeautifulSoup

VERSION = 0.1

class Config(object):
	"""A class containing the configuration for the LEX site"""

	API_PATHS = {
		'login' : 'lex_login.php',
		'search' : 'lex_api_search.php',
		'plugin' : 'lex_filedesc.php?lotGET=%d',
		'dependancy' : 'lex_deptracker.php?LotID=%d',
		'download' : 'lex_filedesc.php?lotDOWNLOAD=%d',
		'add_to_download_list' : 'lex_lotlist_lview.php?cLOTID=%d&addBASKET=T',
		'remove_download_history' : 'lex_downhist.php?rmALLDLHIST=T',
		'lottable' : 'lex_lottable.php',
		'power_search': 'lex_search_00.php'
	}

	BROAD_CATEGORIES = {
		'tools_and_docs' : 'other',
		'mods' : 'mods',
		'maps' : 'map',
		'dependancy' : 'dependancy',
		'lots_and_bats' : 'lotbat',
		'all': 'all'
	}

	def __init__(self, site_name):
		obj = dict({'domain':'sc4devotion.com/csxlex/'})
		self._site_url = "http://" + obj['domain']

		self.user = self.pswd = None


	def __getitem__(self, key):
		"""Return the URL for key."""
		return urljoin(self._site_url, self.API_PATHS[key])

class BaseLEX(object):
	"""A base class that allows access to the LEX API"""

	def __init__(self, user_agent, site_name=None):
		if not user_agent or not(isinstance(user_agent, str)):
			raise TypeError('User agent must be a non-empty string.')

		self.config = Config(site_name or 'LEX')
		self.handler = DefaultHandler()
		self.http = requests.session() # dummy session
		self.http.headers['User-Agent'] = user_agent


	def _request(self, url, params=None, data=None, files=None, auth=None,
		timeout=None):
		"""Given a page url and a dict of params, open and return the page.

		:param url: the url to grab content from.
        :param params: a dictionary containing the GET data to put in the url
        :param data: a dictionary containing the extra data to submit
        :param files: a dictionary specifying the files to upload
        :param auth: Add the HTTP authentication headers (see requests)

        """

		request = _prepare_request(self, url, params, data, auth, files)
		timeout = None

		key_items = []
		for key_value in (params, data, request.cookies, auth):
			if isinstance(key_value, dict):
				key_items.append(tuple(key_value.items()))
			elif isinstance(key_value, cookielib.CookieJar):
				key_items.append(tuple(key_value.get_dict().items()))

		remaining_attemps = 1
		while True:
			try: 
				request.url = url

				response = self.handler.request(request=request.prepare(),
												proxies=self.http.proxies,
												timeout=timeout)
				self.http.cookies.update(response.cookies)
				return response.text
			except requests.exceptions.HTTPError:
				remaining_attemps -= 1
				if remaining_attemps == 0:
					raise

	def _json_lex_objector(self, json_data):
		"""Return appropriate LEXObject from json_data when possible."""

		if 'id' in json_data:
			#print "*** JSON ITEM ***"
			#print json_data
			#print "*****************"
			return objects.Plugin(self, json_data)
		else:
			return json_data

	def _html_lex_objector(self, html_data, *args, **kwargs):
		"""Return appropriate LEXObject from html_data when possible."""
		soup = BeautifulSoup(html_data)

		# Check for form page
		title = soup.find('h4').string
		if title == 'Power Search':
			author_select = soup.find('select', {'id': 'i-author'})
			# options = 
			desired_options = [option for option in author_select.findAll('option') if option.text == kwargs['user_name']]
			for option in desired_options:
				user_json = {'user_name': option.text,
					'id': option['value']}
				print user_json
				return objects.User(self, user_json)


	def request_html(self, url, params=None, data=None, as_objects=True, *args, **kwargs):
		"""Parsing pages that return html. """

		response = self._request(url, params, data)
		if as_objects:
			data = self._html_lex_objector(response, *args, **kwargs)
		else:
			return response
		print data
		return data


	def request_json(self, url, params=None, data=None, as_objects=True):
		response = self._request(url, params, data)

		# Request url just needs to be available for objector to use
		self._request_url = url
		hook = self._json_lex_objector if as_objects else None
		delattr(self, '_request_url')
		data = json.loads(response, object_hook=hook)

		return data

	def login(self, username=None, password=None):
		"""Login to the LEX site."""

		if not password or not username:
			raise Exception('Username and password required.')
        
		data = {'cPASS': password,
			'cUSR': username,
			'cQUICK' : 'true',
			'cENC' : 'false'}
		print self.request_json(self.config['login'], data=data, as_objects=False)
		for c in self.http.cookies:
			print c
		# Update authentication settings
		self._authentication = True
		self.user = self.get_user(username)
		self.user.__class__ = objects.LoggedInUser

	def get_content(self, url, params=None, limit=0, root_field='result'):

		"""A generator method to return LEX content from a URL.

		"""
		fetch_all = fetch_once = False
		objects_found = 0
		params = params or {}

		if url == self.config['search'] and 'broad_type' not in params:
			params['broad_type'] = self.config.BROAD_CATEGORIES['all']
		if limit is None:
			fetch_all = True
			params['limit'] = 30
		elif limit > 0:
			params['limit'] = limit
		else:
			fetch_once = True

		while fetch_once or fetch_all or objects_found < limit:
			
			page_data = self.request_json(url, params=params)
			
			fetch_once = False
			root = page_data.get(root_field, page_data)

			for thing in root:
				yield thing
				objects_found += 1

				if objects_found == limit:
					return
			if objects_found < limit and 'start' not in params:
				params['start'] = objects_found
			elif objects_found < limit and params['start'] < params['limit']:
				params['start'] = objects_found
			else:
				return


	



	@decorators.restrict_access(login=True)
	def download_plugin(self, *args, **kwargs):
		pass

class UnauthenticatedLEX(BaseLEX):
	"""
	This mixin provides bindings for basic functions of the LEX's API.

	None of these functions require authenticated access.
	"""

	def __init__(self, *args, **kwargs):
		super(UnauthenticatedLEX, self).__init__(*args, **kwargs)

	def get_creator(self, user_name, *args, **kwargs):
		
		"""Return a User isntance for the username specified."""

		url = self.config['power_search']
		# return self.get_content(url, params=None, user_name=user_name, *args, **kwargs)
		user = self.request_html(url, params=None, user_name=user_name, *args, **kwargs)
		return user
		

	def get_plugin(self, url=None, plugin_id=None):
		"""Returns a Plugin object for the given url or plugin ID."""

		if bool(url) == bool(plugin_id):
			raise TypeError('Please specify either url or plugin_id, but not both!')
		if plugin_id:
			url = self.config['plugin'] % plugin_id
		return objects.Plugin.from_url(url)

	def get_recent(self, *args, **kwargs ):
		
		"""Return a get_content generator for recent uploads."""
		
		params = {'order_by': 'recent'}
		url = self.config['search']
		return self.get_content(url, params=params, *args, **kwargs)

	def get_popular(self, *args, **kwargs):
		
		"""Return a get_content generator for the most popular uploads."""

		params = {'order_by': 'popular'}
		url = self.config['search']
		return self.get_content(url, params=params, *args, **kwargs)

	def get_updated(self, *args, **kwargs):

		"""Return a get_content generator for recently updated uploads."""

		params = {'order_by': 'update'}
		url = self.config['search']
		return self.get_content(url, params=params, *args, **kwargs)

	def get_category(self, category_name, *args, **kwargs):

		"""Return a Category object for the category_name specified."""
		return objects.Category(self, category_name, *args, **kwargs)



class LEX(UnauthenticatedLEX):
	"""Provides access to the LEX API"""

	

if __name__ == '__main__':
	l = LEX(user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36')
	# l.login(username='pyLEX', password='Bm8QPvan')
	for thing in l.get_recent():
		print thing.fullname



