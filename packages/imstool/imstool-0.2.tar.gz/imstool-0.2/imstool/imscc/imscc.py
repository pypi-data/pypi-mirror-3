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
from imstool.qti import QTIParser1_2
from ccreader import CCReader
from imstool.errors import ManifestError

__author__ = 'Brent Lambert, David Ray, Jon Thomas'
__copyright__ = 'Copyright 2011, enPraxis LLC'

__license__ = 'GPLv2'
__version__ = '$ Revision 0.0 $'[11:-2]
__maintainer__ = 'Brent Lambert'
__email__ = 'brent@enpraxis.net'


class IMSCCReader(IMSReader):
    """ Class for reading IMS CC packages """

    def readPackage(self, zf, objManager):
        objDict = {}
        ccreader = CCReader()
        manifest = self.readManifest(zf)
        if not manifest:
            raise ManifestError, 'Could not locate manifest file.'
        doc = ccreader.parseManifest(manifest)
        objDict['package'] = {}
        orgs = ccreader.readOrganizations(doc)
        resources = ccreader.readResources(doc)
        for x in resources:
            resid, restype, reshref = ccreader.readResourceAttributes(x)
            metadata = ccreader.readMetadata(x)
            files = ccreader.readFiles(x)
            # If the type is a link
            if 'imswl_xmlv1p0' == restype:
                for y in files:
                    hash = resid + y
                    objDict[hash] = metadata
                    id = self.createIdFromFile(y)
                    objDict[hash]['id'] = id.replace('.xml','')
                    objDict[hash]['path'] = self.createPathFromFile(y)
                    linkfile = ccreader.readFile(y)
                    title, location = ccreader.getLinkInfo(linkfile)
                    objDict[hash]['type'] = 'Link'
                    objDict[hash]['title'] = title
                    objDict[hash]['remoteUrl'] = location
            # If the type is QTI 1.2 

            if 'imsqti_xmlv1p2' in restype:
                if files:
                    hash = resid + files[0]
                    qm = self.readManifest(zf, manifestfile=files[0])
                    if qm:
                        objDict[hash] = metadata
                        id = self.createIdFromFile(files[0])
                        objDict[hash]['id'] = id.replace('.xml','')
                        objDict[hash]['path'] = self.createPathFromFile(files[0])
                        objDict[hash]['type'] = 'Quiz'
                        parser = QTIParser1_2()
                        doc = parser.parseManifest(qm)
                        parser.readQTIManifest(doc, objDict[hash])
            # If the type is a file
            elif 'webcontent' == restype:
                for y in files:
                    hash = resid + y
                    # If there is only one file, or it matches the reshref
                    # add the metadata to it if it exists
                    if y == reshref or len(files) == 1:
                        objDict[hash] = metadata
                        # If it is listed in the org section
                        if orgs.has_key(resid):
                            objDict[hash]['position'] = orgs[resid][0]
                            objDict[hash]['excludeFromNav'] = False
                            # Use 'and' as opposed to 'or' to avoid KeyError
                            if not (objDict[hash].has_key('title') and objDict[hash]['title']):
                                objDict[hash]['title'] = orgs[resid][1]
                        else:
                            objDict[hash]['excludeFromNav'] = True
                        objDict[hash]['file'] = y
                        objDict[hash]['type'] = self.determineType(objDict[hash], y)
                    # If it is just a lowly file
                    else:
                        objDict[hash] = {}
                        objDict[hash]['excludeFromNav'] = True
                        objDict[hash]['file'] = y
                        objDict[hash]['type'] = self.determineType(objDict[hash], y)
                    # Add to all files
                    id = self.createIdFromFile(y)
                    if not (objDict[hash].has_key('title') and objDict[hash]['title']):
                        objDict[hash]['title'] = id
                    objDict[hash]['id'] = id
                    objDict[hash]['path'] = self.createPathFromFile(y) 
        if objManager:
            objManager.createObjects(objDict, zf)        


class IMSCCWriter(BaseWriter):
    """ Class for writing IMS CC packages """
