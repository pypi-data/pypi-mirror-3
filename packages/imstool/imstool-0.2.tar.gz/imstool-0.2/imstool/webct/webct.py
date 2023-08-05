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
from webctreader import WebCTReader
from imstool.errors import ManifestError, manifestNotFound

__author__ = 'Brent Lambert, David Ray, Jon Thomas'
__copyright__ = 'Copyright 2011, enPraxis LLC'

__license__ = 'GPLv2'
__version__ = '$ Revision 0.0 $'[11:-2]
__maintainer__ = 'Brent Lambert'
__email__ = 'brent@enpraxis.net'


class IMSWebCTReader(IMSReader):
    """ Class for reading WebCT Packages """

    def readPackage(self, zf, objManager):
        objDict = {}
        webctreader = WebCTReader()
        manifest = self.readManifest(zf)
        if not manifest:
            raise ManifestError, manifestNotFound
        doc = webctreader.parseManifest(manifest)
        manifests = webctreader.readManifests(doc)
        for m in manifests:
            orgs =[]
            manifestmetadata = webctreader.readPackageMetadata(m)
            if manifestmetadata.has_key('webcttype') and manifestmetadata['webcttype'] == 'Course':
                objDict['package'] = manifestmetadata
            else:
                orgs = webctreader.readOrganizations(m)
                resources = webctreader.readResources(m)
                for x in resources:
                    resid, restype, reshref = webctreader.readResourceAttributes(x)
                    files = webctreader.readFiles(x)
                    # If the type is a link
                    if manifestmetadata.has_key('webcttype') and manifestmetadata['webcttype'] == 'URL':
                        for y in files:
                            hash = resid + y
                            objDict[hash] = manifestmetadata
                            id = self.createIdFromFile(y)
                            objDict[hash]['id'] = id
                            objDict[hash]['path'] = ''
                            objDict[hash]['type'] = 'Link'
                            objDict[hash]['remoteUrl'] = y
                    elif restype == 'webcontent':
                        if not files and reshref:
                            files = [reshref,]
                        for y in files:
                            hash = resid + y
                            objDict[hash] = {}
                            # Can apply manifest metadata if single file and single resource
                            if len(resources) == 1 and len(files) == 1:
                                objDict[hash] = manifestmetadata
                            if len(files) == 1:
                                # If it is listed in the org section
                                if orgs.has_key(resid):
                                    objDict[hash]['excludeFromNav'] = False
                                    # Use 'and' as opposed to 'or' to avoid KeyError
                                    if not (objDict[hash].has_key('title') and objDict[hash]['title']):
                                        objDict[hash]['title'] = orgs[resid]
                                else:
                                    objDict[hash]['excludeFromNav'] = True
                                objDict[hash]['file'] = y
                                objDict[hash]['type'] = self.determineType(objDict[hash], y)
                            # If it is just a lowly file
                            else:
                                objDict[hash]['excludeFromNav'] = True
                                objDict[hash]['file'] = y
                                objDict[hash]['type'] = self.determineType(objDict[hash], y)
                            # Add to all files
                            id = self.createIdFromFile(y)
                            objDict[hash]['id'] = id
                            if not (objDict[hash].has_key('title') and objDict[hash]['title']):
                                objDict[hash]['title'] = id
                            objDict[hash]['path'] = self.createPathFromFile(y)
        if objManager:
            objManager.createObjects(objDict, zf)
