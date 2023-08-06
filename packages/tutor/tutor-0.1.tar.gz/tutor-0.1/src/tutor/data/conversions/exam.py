#-*- coding: utf-8 -*-
from tutor.config import schemas
from tutor.data.conversions.base import Import, Parser
from tutor.util.jsonlib import all as jsonlib
from xml.etree.ElementTree import ElementTree

__all__ = [ 'MainImport' ]

#===============================================================================
#                         Importing/Exporting interface
#===============================================================================
class MainImport(Import):
    def load_xml(self, file):
        return XmlMainParser(file).parse()

#===============================================================================
#                                 Parser
#===============================================================================
class XmlMainParser(Parser):
    def parse(self):
        etree = ElementTree()
        etree.parse(self.file)
        json = {}

        # Extract simple properties
        for k, v in schemas.Exam.items(): #@UndefinedVariable
            if isinstance(v, jsonlib.Str):
                v = etree.find(k)
                if v is not None:
                    json[k] = v.text

        # Extract content
        content = []
        for node in (etree.find('content') or []):
            content.append(node.text)
        if content:
            json[u'content'] = content
        return json

if __name__ == '__main__':
    from pprint import pprint
    from tutor.data.raw_lib import LibNode

    ln = LibNode('exam', 'examples', 'simple_exam')
    loc = MainImport()
    with ln.open('main') as F:
        obj = loc.load(F, 'xml')
    pprint(obj)

