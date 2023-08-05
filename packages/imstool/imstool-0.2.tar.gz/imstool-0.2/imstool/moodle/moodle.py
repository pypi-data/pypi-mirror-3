# -*- coding: us-ascii -*-

""" ____________________________________________________________________
 
    This file is part of the imstool software package.

    Copyright (c) 2011 enPraxis, LLC
    http://enpraxis.net

    Portions Copyright (c) 2004-2009 Utah State University
    Portions copyright 2009 Massachusetts Institute of Technology

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, version 2.8  

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
 
    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA 
    _______________________________________________________________________
"""

from imstool.base import IMSReader, BaseWriter
from mbreader import MBReader
from imstool.errors import ManifestError
import re

__author__ = 'Brent Lambert, David Ray, Jon Thomas'
__copyright__ = 'Copyright 2011, enPraxis LLC'

__license__ = 'GPLv2'
__version__ = '$ Revision 0.0 $'[11:-2]
__maintainer__ = 'Brent Lambert'
__email__ = 'brent@enpraxis.net'


class MoodleReader(IMSReader):
    """ Class for reading Moodle backups """

    def readPackage(self, zf, objManager):
        objDict = {}
        mbreader = MBReader()
        manifest = self.readManifest(zf, manifestfile='moodle.xml')
        if not manifest:
            raise ManifestError, 'Could not locate manifest file.'
        doc = mbreader.parseManifest(manifest)
        mods = mbreader.readMods(doc)
        visibleids = mbreader.readSections(doc)
        questions = mbreader.readQuestions(doc)
        for x in mods:
            metadata = {}
            modid = mbreader.readModAttributes(x)
            modtype = mbreader.readModType(x)
            if 'resource' == modtype:
                metadata = mbreader.readResourceMetadata(x)
                if modid:
                    mid = 'resource-' + modid
                    objDict[mid] = metadata
                    if metadata.has_key('file') and metadata['file']:
                        fn = metadata['file'].split('/')[-1]
                    else:
                        fn = modid
                    rtype = self.determineType(metadata, str(fn))
                    fn = unquoteHTML(fn)
                    objDict[mid]['id'] = fn
                    objDict[mid]['type'] = rtype
                    if modid in visibleids:
                        objDict[mid]['excludeFromNav'] = False
                    else:
                        objDict[mid]['excludeFromNav'] = True
            elif 'quiz' == modtype:
                mid = 'quiz-' + modid
                objDict[mid] = {'type':'Quiz',}
                mbreader.getQuizMetadata(x, objDict[mid])
                question_ids = mbreader.getQuestions(x)
                if question_ids:
                    objDict[mid]['items'] = {}
                    objDict[mid]['itemorder'] = []
                    for q in question_ids:
                        if q in questions.keys():
                            objDict[mid]['items'][q] = questions[q]
                            objDict[mid]['itemorder'].append(q)
        if objManager:
            objManager.createObjects(objDict, zf)

        
class MoodleWriter(BaseWriter):
    """ Class for writing Moodle Backups """


def convertHTMLEntity(text):
    """Convert an HTML entity into a string"""
    if text.group(1)=='#':
        try:
            return chr(int(text.group(2)))
        except ValueError:
            return '&#%s;' % text.group(2)
    try:
        return htmlentitydefs.entitydefs[text.group(2)]
    except KeyError:
        return '&%s;' % text.group(2)


def unquoteHTML(text):
    """Convert an HTML quoted string into normal string.
    Works with &#XX; and with &nbsp; &gt; etc."""
    return re.sub(r'&(#?)(.+?);',convertHTMLEntity,text) 
    
