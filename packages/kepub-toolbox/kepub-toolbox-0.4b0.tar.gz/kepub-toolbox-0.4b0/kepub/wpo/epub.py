"""Module for Epub objects manipulation"""

__authors__ = 'Pietro Spagnulo, Stefano Quaranta'
__copyright__ = 'Ecomind S.r.l.'
from kepub import get_version
__version__ = get_version()
__license__ = 'GPLv3'
__mantainer__ = 'Stefano Quaranta'
__email__ = 'steppo40@gmail.com'


class Epub(object):
	"""Define an Epub object in raw XML format"""

	def __init__(self):
		"""Initialize an Epub object"""
		pass

	def compress(self):
		"""Compress an Epub object"""
		pass

	def tweak(self):
		"""Tweak an Epub object"""
		pass

	def check(self):
		"""Check an Epub object"""
		pass
