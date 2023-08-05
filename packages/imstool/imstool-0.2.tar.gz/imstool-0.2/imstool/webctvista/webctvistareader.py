from xml.dom import minidom


class IMSWebCTVistaReader:
    """ Web CT Vista reader """

    def parseManfiest(self, manifest):
        """ read the manifest """
        return minidom.parseString(manifest)
