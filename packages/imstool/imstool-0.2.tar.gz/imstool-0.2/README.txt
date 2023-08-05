Introduction
============

*imstool* is a python library for reading and writing content packages from
a number of open source/proprietary learning management systems, and formal
packaging schemes and standards. It is meant to make importing content from
other learning applications directly into your python programs possible.

History
=======

Code for this library was originally developed for eduCommons 
(http://educommons.com) and consists of code written by 
enPraxis (http://enpraxis.net) as well as code written for the 
OpenCourseWare Consortium (MIT) and Utah State University under 
the Center for Sustainable Learning (COSL).

Using the Library
=================

Reading a Package
-----------------

To read content packages, subclass from the object manager as follows::

    from imstool import BaseObjectManager

    class MyObjectManager(BaseObjectManager):
        """ Read object metadata and file info and create new objects. """

Create a createObject() method in your object manager class that steps
through the objects read by imstool and creates them as needed::

        def createObject(self, objDict, zf):
            """ Step through object metadata and create objects. """

            for oid in objDict:
                data = objDict[oid]
                if 'package' == oid:
                    pass # This is package metadata
                elif 'Document' == data['type']:
                    # Object is a document
                elif 'File' == data['type']:
                    # Object is a File
                elif 'Image' == data['type']:
                    # Object is an Image
                elif 'Quiz' == data['type']:
                    # Object is a quiz/test
                else:
                    # Unknown type

To keep things tidy, you may want to break each type out into a separate
function in the class::

        def createDocument(self, metadata, filedata):
            """ Using metadata in data, create a document """
            ... do some stuff here

and call it from the createObject() method as follows:

            elif 'Document' == data['type']:
                if data.has_key('file'):
                    filedata = self.readFile(zf, data['file'])
                elif data.has_key('text'):
                    filedata = data['text']
                else:
                    filedata = ''
	        self.createDocument(data, filedata)

Once you have your completed object manager class you can set it up
as follows:

    from imstool import importPackage
    from imstool import readers

    nom = MyObjectManager()
    format = readers[0]
    try:
        za = ZipFile(StringIO(package), 'r')
    except BadZipfile, e:
        result = e
    else:
        result = importPackage(za, format, nom)

The *importPackage* method will find the manifest file in the content 
package, parse out any metadata, and will pass the information on to the
object manager class. 

You can get format information from the *readers* object. *readers* is 
a list of tuples containing a friendly name and ID for the type of package that 
is being loaded and parsed. You must include this in the call to 
importPackage() so that the correct parser will be used.

Writing a Package
-----------------

(to be written)

Extending imstool to Support Other Formats
==========================================

(to be written) 



