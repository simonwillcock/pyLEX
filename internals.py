from requests import Request

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
	
def _get_sorted(order='', *args, **kwargs):
	"""Return a function to generate specific plugin listings."""

def _get_user_plugins(user_id='', query='downloaded'):
	"""Return function to generate a list of a User's plugins."""
	def _plugins(self, order='', *args, **kwargs):
		"""Return a get_content generator for some LEXContentObject type."""
		if not user_id:
			user_id = self.user.id
		if query == 'uploaded':
			kwargs.setdefault('params', {})
			kwargs['params'].setdefault('creator', user_id)
