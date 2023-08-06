"""Module for DocBook objects manipulation"""

__authors__ = 'Pietro Spagnulo, Stefano Quaranta'
__copyright__ = 'Ecomind S.r.l.'
from kepub import get_version
__version__ = get_version()
__license__ = 'GPLv3'
__mantainer__ = 'Stefano Quaranta'
__email__ = 'steppo40@gmail.com'


class DocBook(object):
	"""Define a DocBook object in raw XML format"""
	
	def __init__(self): 
		"""Initialize a DocBook object"""
		pass
	
	def to_XML(self, stylesheet):
		"""Convert to styled XML"""
		pass	

	def to_epub(self, stylesheet):
		"""Convert to Epub format through XSL trasformations"""
		pass

	def to_html(self):
		"""Convert to HTML format"""
		pass
