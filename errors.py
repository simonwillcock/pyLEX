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
