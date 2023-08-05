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

from xml.dom import minidom
from imstool.errors import ManifestError
from urlparse import urlparse
from BeautifulSoup import BeautifulSoup

__author__ = 'Brent Lambert, David Ray, Jon Thomas'
__copyright__ = 'Copyright 2011, enPraxis LLC'

__license__ = 'GPLv2'
__version__ = '$ Revision 0.0 $'[11:-2]
__maintainer__ = 'Brent Lambert'
__email__ = 'brent@enpraxis.net'


class MBReader(object):

    def parseManifest(self, manifest):
        """ Parse the moodle xml doc """
        doc = minidom.parseString(manifest)
        moodlebackup = doc.getElementsByTagName('MOODLE_BACKUP')
        if moodlebackup:
            return moodlebackup[0]
        else:
            return None
            
    def readMods(self, main):
        """ Return a list of the resource modules """
        modlist = []
        modules = main.getElementsByTagName('MODULES')
        if modules:
            mods = modules[0].getElementsByTagName('MOD')
            for mod in mods:
                mtype = mod.getElementsByTagName('MODTYPE')[0]
                mt = self.getTextValue(mtype)
                if 'resource' == mt:
                    modlist.append(mod)
                elif 'quiz' == mt:
                    modlist.append(mod)
        return modlist

    def readModAttributes(self, mod):
        """ Return the id of the current module """
        id_elem = mod.getElementsByTagName('ID')[0]
        if id_elem:
            return self.getTextValue(id_elem)
        return ''

    def readModType(self, mod):
        mtype_elem = mod.getElementsByTagName('MODTYPE')[0]
        if mtype_elem:
            return self.getTextValue(mtype_elem)
        return ''

    def readSections(self, main):
        """ Returns a list of visible resources  """
        visids = []
        sections = main.getElementsByTagName('SECTIONS')
        if sections:
            sectionelements = sections[0].getElementsByTagName('SECTION')
            for sectionelement in sectionelements:
                mods = sectionelement.getElementsByTagName('MODS')
                if mods:
                    modelements = mods[0].getElementsByTagName('MOD')
                    for modelement in modelements:
                        # If the resource module is marked visible within
                        # a top level (indent) then place it in navigation.
                        type = modelement.getElementsByTagName('TYPE')[0]
                        if self.getTextValue(type) == 'resource':
                            if self.getTextValue(modelement.getElementsByTagName('VISIBLE')[0]) == '1':
                                if self.getTextValue(modelement.getElementsByTagName('INDENT')[0]) == '0':
                                    id = self.getTextValue(modelement.getElementsByTagName('INSTANCE')[0])
                                    if id not in visids:
                                        visids.append(id)
        return visids

    def readQuestions(self, main):
        """ Returns a list of questions to be matched up with the quiz object. """
        questions = {}
        qcat = main.getElementsByTagName('QUESTION_CATEGORIES')
        if qcat:
            qcs = qcat[0].getElementsByTagName('QUESTION_CATEGORY')
            for qc in qcs: 
                questions_node = qc.getElementsByTagName('QUESTIONS')
                if questions_node:
                    qs = questions_node[0].getElementsByTagName('QUESTION')
                    for q in qs:
                        id_node = q.getElementsByTagName('ID')
                        if id_node:
                            qid = self.getTextValue(id_node[0])
                            title_node = q.getElementsByTagName('NAME')
                            if title_node:
                                title = self.getTextValue(title_node[0])
                                qt = self.readQuestionType(q)
                                if 'multichoice' == qt:
                                    questions[qid] = {'title':title, 
                                                      'questiontype':'Multiple Choice',}
                                    self.readQuestion(q, questions[qid])
                                    self.readResponses(q, questions[qid])
                                elif 'truefalse' == qt:
                                    questions[qid] = {'title':title, 
                                                      'questiontype':'True/False',}
                                    self.readQuestion(q, questions[qid])
                                    self.readResponses(q, questions[qid])
                                elif 'essay' == qt:
                                    questions[qid] = {'title':title,
                                                      'questiontype':'Essay',}
                                    self.readQuestion(q, questions[qid])
                                    
        return questions
                    
    def readQuestionType(self, node):
        """ Read question metadata """
        qt = 'Unknown'
        qtype_node = node.getElementsByTagName('QTYPE')
        if qtype_node:
            qt = self.getTextValue(qtype_node[0])
        return qt
            

    def readQuestion(self, node, data):
        """ Read a individual question """
        qtext_node = node.getElementsByTagName('QUESTIONTEXT')
        if qtext_node:
            qtext = self.getTextValue(qtext_node[0])
            qtype_node = node.getElementsByTagName('QUESTIONTEXTFORMAT')
            if qtype_node:
                qtype = self.getTextValue(qtype_node[0])
                data['question'] = qtext
                data['qtexttype'] = qtype

    def readResponses(self, node, data):
        """ Get responses """
        data['responses'] = []
        data['cresponse'] = []
        answers = node.getElementsByTagName('ANSWERS')
        for ans in answers:
            if 'QUESTION' == ans.parentNode.tagName:
                answer = ans.getElementsByTagName('ANSWER')
                for an in answer:
                    id_node = an.getElementsByTagName('ID')
                    respid = self.getTextValue(id_node[0])
                    atext_node = an.getElementsByTagName('ANSWER_TEXT')
                    if atext_node:
                        atext = self.getTextValue(atext_node[0])
                        data['responses'].append(
                            (respid,
                             {'rtexttype':'text/html', 'response':atext,}))
                        fr_node = an.getElementsByTagName('FRACTION')
                        if fr_node:
                            fr = self.getTextValue(fr_node[0])
                            if fr != '0':
                                data['cresponse'].append(respid)
                        
                                    

    def getQuestions(self, node):
        """ Get questions for the quiz. """
        questions = []
        qi_node = node.getElementsByTagName('QUESTION_INSTANCES')
        if qi_node:
            qi_nodes = qi_node[0].getElementsByTagName('QUESTION_INSTANCE')
            for q in qi_nodes:
                qnode = q.getElementsByTagName('QUESTION')
                if qnode:
                    questions.append(self.getTextValue(qnode[0]))
        return questions

    def getQuizMetadata(self, node, data):
        """ Get Quiz metadata """
        id_node = node.getElementsByTagName('ID')
        for qid in id_node:
            if 'MOD' == qid.parentNode.tagName:
                data['id'] = self.getTextValue(qid)
                break
        name_node = node.getElementsByTagName('NAME')
        for n in name_node:
            if 'MOD' == n.parentNode.tagName:
                data['title'] = self.getTextValue(n)
                break

    def readResourceMetadata(self, mod):
        """ Read in the resource module """
        metadata = {}
        reference = ''
        refnode = mod.getElementsByTagName('REFERENCE')
        if refnode and self.getTextValue(refnode[0]):
            reference = self.getTextValue(refnode[0])
            if reference:
                reference = self.runFilters(reference, ['variables'])
        title = mod.getElementsByTagName('NAME')
        metadata['title'] = self.getTextValue(title[0])
        type = self.getTextValue(mod.getElementsByTagName('TYPE')[0])
        if type == 'text':
            metadata['Format'] = 'text/plain'
        elif type == 'html':
            metadata['Format'] = 'text/html'
        elif type == 'file' and reference:
            parsedurl = urlparse(reference)
            if parsedurl[0]:
                metadata['remoteUrl'] = reference
                metadata['type'] = 'Link'
            else:
                metadata['file'] = 'course_files/%s' %reference
        else:
            metadata['Format'] = 'text/html'
            metadata['text'] = ''
        summary = mod.getElementsByTagName('SUMMARY')
        if summary:
            descrip = self.getTextValue(summary[0])
            if descrip:
                metadata['description'] = self.runFilters(descrip, ['striphtml'])
        alltext = mod.getElementsByTagName('ALLTEXT')
        if alltext:
            text = self.getTextValue(alltext[0])
            if text:
                metadata['text'] = self.runFilters(text, ['variables'])
        metadata['path'] = ''
        return metadata

    def runFilters(self, text, filters):
        """ Run a filter over the links """
        rettext = text
        if 'variables' in filters:
            rettext = self.removeMoodleVariables(rettext)
        if 'striphtml' in filters:
            rettext = self.stripHTML(rettext)
        return rettext
        
    def removeMoodleVariables(self, text):
        """ Remove all the moodle variables """
        import re
        return re.sub('\$@.*@\$','', text)
    
    def stripHTML(self, text):
        """ Remove all html tags and return the inner text """
        import re
        return re.sub('<([^!>]([^>]|\n)*)>','', text)

    def getTextValue(self, node):
        """ Removes the text from the text_node of a node """
        for x in node.childNodes:
            if x.nodeType == x.TEXT_NODE:
                return x.nodeValue.strip()
        return None
