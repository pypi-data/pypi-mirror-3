"""Provide useful tools for XML documents transformation"""

__authors__ = 'Pietro Spagnulo, Stefano Quaranta'
__copyright__ = 'Ecomind S.r.l.'
from kepub import get_version
__version__ = get_version()
__license__ = 'GPLv3'
__mantainer__ = 'Stefano Quaranta'
__email__ = 'steppo40@gmail.com'

import os
import subprocess
import time
import shlex

from kepub.error import TransformationError

import logging
logger = logging.getLogger(__name__)

SAXON_CLASSPATH = os.path.join (os.path.dirname(__file__), 'sax', 'saxon9he.jar')
SLEEP_TIME = 0

def transform(src_file, xsl_file, dst_file=os.path.join(os.getcwd(),'output.xml')):
    """Utility function for Saxon XSL transformation
    
    src_file - XML source file
    xsl_file - XSL file to be applied by Saxon
    dst_file - XML output file (default to "output.xml" in the script execution current directory)
    """
    
    try:
        if logger: logger.debug('Applying transformation with XSLT stylesheet module %s' % xsl_file)
        cmd = 'java -classpath "%s" net.sf.saxon.Transform -s:"%s" -xsl:"%s" -o:"%s"' % \
              (SAXON_CLASSPATH, src_file, xsl_file, dst_file)
        dummy_file = open(os.devnull, 'w')
        subprocess.call(shlex.split(cmd), stderr=dummy_file)
        time.sleep(SLEEP_TIME)
    except subprocess.CalledProcessError as cpe:
        raise TransformationError(cpe)
    except OSError as ose:
        raise TransformationError(ose)
