from imstool.base import IMSReader
from webctvistareader import IMSWebCTVistaReader
from imstool.errors import ManifestError, manifestNotFound


class IMSWebCTVistaReader(IMSReader):
    """ Web CT Vista Reader """

    def readPackage(self, zf, objManager):
        """ read a Web CT Vista Package """
    
