import socket
from requests import Session
from errors import ClientException

class DefaultHandler(object):

	def __init__(self):
		self.http = Session() # Each instance should have it's own session

	def request(self, request, **_):
		return self.http.send(request, allow_redirects=False)
