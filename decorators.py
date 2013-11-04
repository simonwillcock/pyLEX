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