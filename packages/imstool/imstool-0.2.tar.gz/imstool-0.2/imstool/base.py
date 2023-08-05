# -*- coding: us-ascii -*-

""" ____________________________________________________________________
 
    This file is part of the imstool software package.

    Copyright (c) 2011 enPraxis, LLC
    http://enpraxis.net

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

from mimetypes import guess_type

__author__ = 'Brent Lambert'
__copyright__ = 'Copyright 2011, enPraxis LLC'

__license__ = 'GPLv2'
__version__ = '$ Revision 0.0 $'[11:-2]
__maintainer__ = 'Brent Lambert'
__email__ = 'brent@enpraxis.net'

class BaseReader:
    """ Base class for reading packages """

    def readPackage(self, zf, objManager):
        """ Read package data """
        manifest = self.readManifest(zf)
        objDict = {}
        if objManager:
            objManager.createObjects(objDict, zf)

    def readManifest(self, zf, manifestfile='imsmanifest.xml'):
        """ Find and read the manifest out of the Zip archive. """
        if zf:
            for x in zf.namelist():
                index = x.find(manifestfile)
                if index != -1:
                    return zf.read(x)
        return None


class IMSReader(BaseReader):
    """ IMS Reader base class for IMS style packages. """

    # Helper functions for readPackage
    def createIdFromFile(self, file):
        """ Get Id from file path """
        return file.split('/')[-1]

    def createPathFromFile(self, file):
        """ Get folder path from file path """
        return '/'.join(file.split('/')[:-1])

    def determineType(self, item, fn):
        """ Determine the type of the item """
        result = 'File'
        docmimetypes = [
            'text/html', 
            'text/htm', 
            'text/plain', 
            'text/x-rst', 
            'text/structured'
            ]
        if item.has_key('type') and item['type']:
            result = item['type']
        elif item.has_key('Format') and item['Format'] in docmimetypes:
            result = 'Document'
        elif item.has_key('Format') and 'image' in item['Format']:
            result = 'Image'
        else:
            mimetype = guess_type(fn)
            if type(mimetype) == type(()) and len(mimetype):
                mimetype = mimetype[0]
            if mimetype in docmimetypes:
                result = 'Document'
            elif mimetype and 'image' in str(mimetype):
                result = 'Image'
        return result              


class BaseWriter:
    """ Base class for writing packages """

    def writeObjectDataToPackage(self, zf, objdata):
        """ Write package data """

class BaseObjectManager:
    """ Base class for managing content to and from a packager. """

    def readObjectData(self, objdata):
        """ Process data generated from readPackage() method in reader """

    def createObjects(self, objDict, zf):
        """ Create objects parsed from imstool """
        
    def readFile(self, zf, fn):
        """ Read a file out of the zip archive """
        f = zf.open(fn, 'r')
        data = f.read()
        f.close()
        return data
