from zope.interface import implements
from Products.Five.browser import BrowserView
from interfaces import IAnonymousView
try:
	from zope.app.zapi import absoluteURL
except ImportError:
	from zope.traversing.browser import absoluteURL
import urllib2

class AnonymousView(BrowserView):
	implements(IAnonymousView)
	
	def __call__(self):
		url = absoluteURL(self.context, self.request)
		response = urllib2.urlopen(url)
		return response.read()