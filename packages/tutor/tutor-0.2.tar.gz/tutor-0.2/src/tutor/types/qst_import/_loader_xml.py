#-*- coding: utf-8 -*-
from xml.etree import ElementTree as etree
from tutor.shared_db.jsoe_util import Converter

def xml_to_jsoe(xml):
    """Convert XML file representing question to JSOE (JavaScript Object 
    Equivalent)"""
    
    # if XML is a string, creates a file object 
    if isinstance(xml, basestring):
        xml = open(xml, 'r')
    
    # parse XML
    xml = etree.parse(xml)    
    return XMLConverter(xml).jsoe 

#------------------------------------------------------------------------------
#    Class extract features
#------------------------------------------------------------------------------
class XMLConverter(Converter):
    def __init__(self, xml):
        super(XMLConverter, self).__init__()
        self.xml = xml
        for elem in self.xml.getroot():
            elem = getattr(self, elem.tag)(elem)
            if elem:
                self.elems.append(elem)
        self.jsoe['data'] = self.elems

    # --- Metainformation elements --------------------------------------------
    def root(self, elem):
        """Extracts the metadata dictionary"""
        
        meta_dic = {}
        
        # extract nodes
        for node in elem:
            tag = node.tag
            try:
                meta_dic[tag] = getattr(self, 'meta_' + tag)(node)
            except AttributeError:
                meta_dic[tag] = node.text
      
        self.jsoe['root'] = meta_dic

    def meta_date(self, node):
        day = int(node.find('day').text)
        month = int(node.find('month').text)
        year = int(node.find('year').text)
        return (year, month, day)
    
    def meta_difficulty(self, node):
        return float(node.text)

    # --- Global feedback ------------------------------------------------------
    def feedback(self, elem):
        elems = [ (x.tag, x.text) for x in elem ]
        self.jsoe['feedback'] = dict(elems)

    # --- Question environment: multiplechoice ---------------------------------
    def code(self, elem):
        return { 'type': 'code', 
                 'src': elem.text,
                 'language': elem.get('language', 'python') }
     
    def intro(self, elem):
        """Extracts the info element"""
    
        return { 'type': 'intro',
                 'text': elem.text }
        
    def multiplechoice(self, elem):
        # extract stem from items
        stem = elem.find('stem')
        try:
            elem.remove(stem)
            stem = stem.text
        except AttributeError:
            stem = None
         
        # process items    
        item_fmt = self.multiplechoice_item
        items = [ item_fmt(node) for node in elem ]
        shuffle = elem.get('shuffle', 'true').lower()
        shuffle = {'true': True, 'false': False }[shuffle]
        return { 'type': 'multiplechoice',
                 'stem': stem,
                 'items': items,
                 'shuffle': shuffle }

    def multiplechoice_item(self, elem):
        # process item in multiplechoice environment
        text = self.extract_text(elem.find('text'), 'text')
        feedback = self.extract_text(elem.find('feedback'), 'feedback')
        comment = self.extract_text(elem.find('comment'), 'comment')
        grade = elem.get('grade', 0)
        return dict([ text, feedback, comment, ('grade', grade) ])
            
    def extract_text(self, elem, tag=None):
        """Extracts the text from element named name. 
        
        Returns the list [name, elem] and feed code to self.elems."""
        
        if elem is None:
            return (tag, None)
        
        if len(elem) > 0:
            text = [ elem.text if elem.text else '' ]
            for e in elem:
                self.var_idx += 1
                name = e.text.strip()
                var_dic = { 'type': 'var',
                            'name': name,
                            'idx': self.var_idx,
                            'filter': e.get('filter', 'default'),
                            'sign': e.get('sign', None),
                            'braces': e.get('braces', False) }
                self.elems.append(var_dic)
                text.append('%%(var_%s)s' % self.var_idx)
                if e.tail:
                    text.append(e.tail)
            text = ''.join(text)
            tag = elem.tag + '()'
        else:
            tag = elem.tag
            text = elem.text
        
        return (tag, text)
        
#------------------------------------------------------------------------------
if __name__ == '__main__':
    import pprint
    #pprint.pprint(xml_to_jsoe('demo_nopy.xml'))
    pprint.pprint(xml_to_jsoe('demo.xml'))