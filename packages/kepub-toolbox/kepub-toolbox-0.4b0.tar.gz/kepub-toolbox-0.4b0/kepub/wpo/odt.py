"""Module for OpenOffice document objects manipulation"""

from __future__ import with_statement

__authors__ = 'Pietro Spagnulo, Stefano Quaranta'
__copyright__ = 'Ecomind S.r.l.'
from kepub import get_version
__version__ = get_version()
__license__ = 'GPLv3'
__mantainer__ = 'Stefano Quaranta'
__email__ = 'steppo40@gmail.com'

from kepub import get_version
__version__ = get_version()

import os
import tempfile
from shutil import copy
from zipfile import ZipFile, is_zipfile
import codecs
import re
import logging

import kepub
from kepub import utils
from kepub.error import TransformationError

MOD_PATH = os.path.dirname(kepub.__file__)
logger = logging.getLogger(__name__)


class Odt(object):
    """Define an OpenOffice document object in raw XML format"""

    def __init__(self, odtfile):
        try:
            self.f = odtfile
            logger.info('Processing file %s' % self.f)
            self.wrk_path = tempfile.mkdtemp(prefix='kepub')
            logger.debug('Working folder is %s' % self.wrk_path)
            if is_zipfile(self.f):
                logger.debug('Decompressing odt file')
                zf = ZipFile(self.f)
                logger.debug('Extracting content from compressed odt file %s' % odtfile)
                for name in zf.namelist():
                    if name.startswith('Pictures'):
                        zf.extract(name, self.wrk_path)
                zf.extract('content.xml', self.wrk_path)
                zf.close()
            else:
                logger.debug('Using direct XML content file')
                copy(self.f, os.path.join(self.wrk_path, 'content.xml'))
        except TypeError as te:
            logger.critical(te)
            raise te
        except IOError as ioe:
            logger.critical(ioe)
            raise ioe
        except OSError as ose:
            logger.critical(ose)
            raise ioe
        except:
            raise

    def to_docbook(self, output_folder=os.path.join(os.getcwd(), 'docbook')):
        """Convert object to a valid DocBook XML file
        
        Attributes:
            output_folder -- folder path for generated output files (default: 'docbook')
            
        """
        
        try:
            logger.info('Applying transformations from Odt to DocBook file object')
            xsl_path = os.path.join(MOD_PATH, 'xsl', 'odt2docbook')
            logger.debug('XSLT stylesheet modules path is %s' % xsl_path)
            src_filepath = os.path.join(self.wrk_path, 'content.xml')
            xsl_filepath = os.path.join(xsl_path, 'odt2docbook1.xsl')
            dst_filepath = os.path.join(self.wrk_path, 'temp1.xml') 
            utils.transform(src_filepath, xsl_filepath, dst_filepath)
            for r in range(6):
                src_filepath = os.path.join(self.wrk_path, 'temp%d.xml' % (r+1,))
                xsl_filepath = os.path.join(xsl_path, 'odt2docbook%d.xsl' % (r+2,))
                dst_filepath = os.path.join(self.wrk_path, 'temp%s.xml' % (r+2,))
                utils.transform(src_filepath, xsl_filepath, dst_filepath)
            #tweaking
            input_filename = os.path.join(self.wrk_path, dst_filepath)
            output_filename = os.path.join(self.wrk_path, 'tweaked_docbook.xml')
            self._tweak(input_filename, output_filename)
            #final copy from temporary to output folder
            try:
                os.makedirs(output_folder)
                img_path = os.path.join(self.wrk_path, 'Pictures')
                if os.path.exists(img_path):
                    os.makedirs(os.path.join(output_folder, 'images'))
                    for img_file in os.listdir(img_path):
                        copy(os.path.join(img_path, img_file), os.path.join(output_folder, 'images', img_file))
                copy(output_filename, os.path.join(output_folder, os.path.splitext(self.f)[0] + '.xml'))
            except OSError as ose:
                logger.error('Could not create output folder %s', output_folder)
                logger.error('Intermediate output files left in %s', self.wrk_path)
        except TransformationError as te:
            logger.critical(te.msg)
            raise te
        except OSError as ose:
            logger.critical(ose)
            raise ose
        except IOError as ioe:
            logger.critical(ioe)
            raise ioe

    def _tweak(self, input_file, output_file, regex_filename=os.path.join(MOD_PATH, 're','subs.txt'), delimiter=' '):
        logger.info('Applying regex substitution tweaks')
        try:
            re_file = open(regex_filename, 'r')
            re_list = []
            for re_line in re_file:
                if len(re_line) > 0 and re_line.lstrip()[0] != '#':
                    try:
                        re_list.append(re_line.strip().split(delimiter))
                    except:
                        logger.error('Error while loading regex patterns: %s' % re_line)
            logger.debug('Loaded regex patterns: %s' % re_list)
            re_file.close()
            with codecs.open(input_file, 'r', encoding="utf-8") as r:
                with codecs.open(output_file, 'w', encoding="utf-8") as w: 
                    lines = r.readlines()
                    for line in lines:
                        for re_item in re_list:
                            if len(re_item) == 1:
                                line = re.sub(re_item[0], '', line)
                            elif len(re_item) == 2:
                                line = re.sub(re_item[0], re_item[1], line)
                            else:
                                logger.warning('Unrecognized substitution pattern: %s' % re_item)
                        w.write(line)
        except IOError as ioe:
            logger.error(ioe)
