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

from xml.dom import minidom

__author__ = 'Brent Lambert'
__copyright__ = 'Copyright 2011, enPraxis LLC'

__license__ = 'GPLv2'
__version__ = '$ Revision 0.0 $'[11:-2]
__maintainer__ = 'Brent Lambert'
__email__ = 'brent@enpraxis.net'


class QTIParser1_2:
    """ Parse QTI 1.2 """
    
    def parseManifest(self, manifest):
        """ parse the QTI manifest """
        return minidom.parseString(manifest)


    def readQTIManifest(self, manifest, data):
        """ Read data out of the manifest and store it in data """
        assessment = manifest.getElementsByTagName('assessment')
        if assessment:
            data['title'] = assessment[0].getAttribute('title')
            sections = assessment[0].getElementsByTagName('section')
            for s in sections:
                items = s.getElementsByTagName('item')
                data['items'] = {}
                data['itemorder'] = []
                for i in items:
                    self.readItem(i, data['items'], data['itemorder'])

    def readItem(self, item, data, order):
        """ Read an item out of the manifest. """
        
        itemid = item.getAttribute('ident')
        if itemid:
            order.append(itemid)
            data[itemid] = {}
            itemtitle = item.getAttribute('title')
            if itemtitle:
                data[itemid]['title'] = itemtitle
            self.readItemMetadata(item, data[itemid])
            self.readPresentation(item, data[itemid])
            self.readProcessingInfo(item, data[itemid])
        
    def readItemMetadata(self, item, data):
        """ Read the item's metadata """
        metadata = item.getElementsByTagName('qtimetadata')
        for m in metadata:
            fields = m.getElementsByTagName('qtimetadatafield')
            for f in fields:
                flabel = f.getElementsByTagName('fieldlabel')
                if flabel:
                    label = self.getTextValue(flabel[0])
                    fentry = f.getElementsByTagName('fieldentry')
                    if fentry:
                        entry = self.getTextValue(fentry[0])
                        if label:
                            if 'qmd_questiontype' == label:
                                if 'Multiple-choice' == entry:
                                    data['questiontype'] = 'Multiple Choice'
                                if 'Multiple-response' == entry:
                                    data['questiontype'] = 'Multiple Answer'
                                if 'True/false' == entry:
                                    data['questiontype'] = 'True/False'
                                if 'FIB-string' == entry:
                                    data['questiontype'] = 'Essay'
                            elif 'cc_profile' == label:
                                if 'cc.multiple_choice.v0p1' == entry:
                                    data['questiontype'] = 'Multiple Choice'
                                if 'cc.multiple_response.v0p1' == entry:
                                    data['questiontype'] = 'Multiple Answer'
                                if 'cc.true_false.v0p1' == entry:
                                    data['questiontype'] = 'True/False'
                                if 'cc.essay.v0p1' == entry:
                                    data['questiontype'] = 'Essay'
                            elif 'cc_weighting' == label:
                                data['questionscore'] = entry
                                
        if not data.has_key('questiontype'):
            data['questiontype'] = 'Unknown'
        

    def readPresentation(self, item, data):
        """ Read the item's presentation data """
        presentation = item.getElementsByTagName('presentation')
        for p in presentation:
            flow = p.getElementsByTagName('flow')
            if flow:
                for f in flow:
                    self.readQuestion(f, data)
                    self.readResponses(f, data)
            else:
                self.readQuestion(p, data)
                self.readResponses(p, data)

    def readQuestion(self, flow, data):
        """ Read the Question """
        material = flow.getElementsByTagName('material')
        if material and len(material) > 0:
            text, ttype = self.readMaterial(material[0])
            data['qtexttype'] = ttype
            data['question'] = text
                
    def readResponses(self, flow, data):
        """ Read responses """
        data['responses'] = []
        responses = flow.getElementsByTagName('response_lid')
        if responses:
            choice = responses[0].getElementsByTagName('render_choice')
            if choice:
                labels = choice[0].getElementsByTagName('response_label')
                for x in labels:
                    respid = x.getAttribute('ident')
                    if respid:
                        material = x.getElementsByTagName('material')
                        if material:
                            text, ttype = self.readMaterial(material[0])
                            data['responses'].append(
                                (respid,
                                 {'rtexttype':ttype, 'response':text, }))
                        

    def readProcessingInfo(self, item, data):
        """ Read processing info """
        resprocessing = item.getElementsByTagName('resprocessing')
        if resprocessing:
            rcond = resprocessing[0].getElementsByTagName('respcondition')
            for c in rcond:
                title = c.getAttribute('title')
                if title and title in ['CorrectResponse', 'Correct']:
                    veq = c.getElementsByTagName('varequal')
                    if veq:
                        if data.has_key('cresponse'):
                            data['cresponse'].append(self.getTextValue(veq[0]))
                        else:
                            data['cresponse'] = [self.getTextValue(veq[0])]
                

    def readMaterial(self, mat):
        text = None
        ttype = None
        mattext = mat.getElementsByTagName('mattext')
        if mattext:
            ttype = mattext[0].getAttribute('texttype')
            text = self.getTextValue(mattext[0])
        return text, ttype
                

    def getTextValue(self, node):
        """ Get text value out of node. """
        for x in node.childNodes:
            if x.TEXT_NODE == x.nodeType:
                return x.nodeValue.strip()
        return None
                    
                
