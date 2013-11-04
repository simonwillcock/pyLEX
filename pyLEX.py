import sys
import requests
import cookielib
import json
import errors
from requests.compat import urljoin
from requests import Request
from handlers import DefaultHandler
from internals import _prepare_request
from objects import Plugin

class Config(object):
	"""A class containing the configuration for the LEX site"""

	API_PATHS = {
		'login' : 'lex_login.php',
		'search' : 'lex_api_search.php',
		'plugin' : 'lex_filedesc.php?lotGET=%s'
	}

	def __init__(self, site_name):
		self._site_url = "http://sc4devotion.com/csxlex/"

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
			return Plugin(self, json_data)
		else:
			return json_data


	def request_json(self, url, params=None, data=None, as_objects=True):
		response = self._request(url, params, data)

		# Request url just needs to be available for objector to use
		#print "*** RESPONSE ***"
		#print response
		#print "****************"
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

	def get_content(self, url, params=None, limit=0, root_field='result'):
		objects_found = 0
		params = params or {}
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

			return


	def get_recent(self, *args, **kwargs ):
		"""Return a get_content generator for recent uploads."""
		params = {'order_by': 'recent',
		'broad_type' : 'all'}

		url = self.config['search']
		return self.get_content(url, params=params, *args, **kwargs)

class LEX(BaseLEX):
	"""Provides access to the LEX API"""

	

if __name__ == '__main__':
	l = LEX(user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36')
	# l.login(username='pyLEX', password='Bm8QPvan')
	for thing in l.get_recent():
		print thing.fullname


