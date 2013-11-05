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


import json
from requests.compat import urljoin
from internals import _get_user_plugins, _get_sorter


class LEXContentObject(object):
	
	"""Base class that represents actual LEX objects."""

	def __init__(self,lex_session, json_dict=None, fetch=True):
		self.lex_session= lex_session
		self.has_fetched = self._populate(json_dict, fetch)

	def __eq__(self, other):
		return (isinstance(other, LEXContentObject) and self.fullname == other.fullname)
	
	def __ne__(self, other):
		return not (self == other)

	def __getattr__(self, attr):
		if not self.has_fetched:
			self.has_fetched = self._populate(None, True)
			return getattr(self, attr)
		raise AttributeError('\'%s\' has no attribute \'%s\'' % (type(self),
																attr))
	def __str__(self):
		strname = self.__unicode__()
		strname = strname.encode('utf-8')
		return strname

	def __setattr__(self, name, value):
		super(LEXContentObject, self).__setattr__(name, value)

	def from_api_response(cls, lex_session, json_dict):
		"""Return an instance of the appropriate class from the json_dict."""
		return cls(lex_session, json_dict=json_dict)

	def _populate(self, json_dict, fetch):
		if json_dict is None:
			json_dict = {}

		for name, value in json_dict.iteritems():
			if name == 'author':
				value = self.get_creator(user_name=value)
			setattr(self, name, value)
		return bool(json_dict) or fetch

class Plugin(LEXContentObject):
	
	"""A class for plugins uploaded to LEX"""
	

	def __init__(self, lex_session, json_dict):
		super(Plugin, self).__init__(lex_session, json_dict)

		# self.permalink = urljoin(lex_session.config['plugin'], self.id)

	def __repr__(self):
		return 'Plugin(name=\'{0}\', version=\'{1}\', author=\'{2}\')'.format(self.name, 
															self.version, self.author)

	def __unicode__(self):
		fullname = self.fullname.replace('\r\n', ' ')
		return fullname

	@staticmethod
	def from_url(lex_session, url):
		pass

	@property
	def fullname(self):
		"""Returns the object's fullname

		The full name consists of the name like 'N.A.M' followed by
		the version in parenthesis like '(v. 1.0)' followed by
		the author such as 'by NAM Team'
		"""
		return '%s (v. %s) by %s' % (self.name, self.version, self.author)


	def from_url(lex_session, url):
		"""Request the URL and return a Plugin object.

		Requires parsing HTML to get data."""

		pass
		# params = {}
		# plugin_info = reddit_session, request_json(url, params=params)

class Category(LEXContentObject):
	"""A class representing a LEX category.

	These are somewhat fake as you can't query categories on LEX currently
	but it is structured this way to make for more intuitive usage 
	such as c = l.get_category('maps').get_recent(limit=10).
	"""

	def __init__(self, lex_session, name):
		super(Category, self).__init__(lex_session, None, False)
		if name in lex_session.config.BROAD_CATEGORIES:
			self.name = lex_session.config.BROAD_CATEGORIES[name]
		else:
			raise TypeError('`s` is not a valid category.')
		self._url = lex_session.config['search']
		self._params = {'broad_type': self.name}

	def __str__(self):
		return self.config.BROAD_CATEGORIES[name]

	def __repr__(self):
		return 'Category(name=`{0}`)'.format(self.name)

	get_recent = _get_sorter('recent')
	get_updated = _get_sorter('update')
	get_popular = _get_sorter('popular')

class User(LEXContentObject):

	"""A class representing a LEX user."""

	def __init__(self, lex_session, json_dict, user_name=None, user_id=None):

		super(User, self).__init__(lex_session, json_dict, False)
		
		self._url = lex_session.config['search']
		self._params = {'creator': self.id}

	def __unicode__(self):
		return self.user_name
	
	get_uploaded = get_uploaded_by_recent = _get_sorter('recent')
	get_uploaded_by_popular = _get_sorter('popular')
	get_uploaded_by_updated = _get_sorter('update')

	# get_uploaded = _get_user_plugins('uploaded')
	# get_downloaded = _get_user_plugins('downloaded')

	def _get_user_info(user_name=None, user_id=None):
		
		"""Find user_name or user_id from LEX."""

		if bool(user_name) == bool(user_id):
			raise TypeError('One (and only one) of user_name or user_id is required!')
	



class LoggedInUser(User):

	"""A class representing an authenticated LEX user."""




"""
import praw
>>> r = praw.Reddit(user_agent='my_cool_application')
>>> submissions = r.get_subreddit('opensource').get_hot(limit=5)
>>> [str(x) for x in submissions]
"""