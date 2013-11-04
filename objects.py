import json
from requests.compat import urljoin


class LEXContentObject(object):
	
	"""Base class that represents actual LEX objects."""

	def __init__(self,lex_session, json_dict=None, fetch=True):
		self.lex_sessionlex_session = lex_session
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
			setattr(self, name, value)
		return bool(json_dict) or fetch

class Plugin(LEXContentObject):
	
	"""A class for plugins uploaded to LEX"""
	@staticmethod
	def from_url(lex_session, url):
		pass

	def __init__(self, lex_session, json_dict):
		super(Plugin, self).__init__(lex_session, json_dict)

		# self.permalink = urljoin(lex_session.config['plugin'], self.id)



	def __unicode__(self):
		fullname = self.fullname.replace('\r\n', ' ')
		return fullname


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





"""
import praw
>>> r = praw.Reddit(user_agent='my_cool_application')
>>> submissions = r.get_subreddit('opensource').get_hot(limit=5)
>>> [str(x) for x in submissions]
"""