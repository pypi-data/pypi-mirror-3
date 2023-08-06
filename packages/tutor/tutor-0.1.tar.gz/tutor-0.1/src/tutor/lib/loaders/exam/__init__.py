#-*- coding: utf-8 -*-
from xml.etree.ElementTree import ElementTree
from tutor.config import schemas
from tutor.lib import Addr
from tutor.util.jsonlib import Str

DEBUG = False
#DEBUG = True

#===============================================================================
#                 Mapping: type -> from_...() functions
#===============================================================================
EXAM_LOADERS = {}
def exam_loader(func):
    ext = func.func_name.split('_')[1]
    EXAM_LOADERS[ext] = func
    return func

def from_addr(addr, validate=True, ret_modified=False, **kwds):
    # Import the JSON structure from the template's view
    addr_path = addr
    addr = Addr(addr, base='exam')
    view = addr.get_data()
    loader = EXAM_LOADERS[addr.get_data_type()]
    json_obj = loader(view, validate=False, **kwds)
    json_obj['name'] = addr_path
    json_obj.setdefault('is_template', True)
    if validate:
        schemas.Exam.validate(json_obj, require_defaults=False)
    if ret_modified:
        return json_obj, addr.get_mtime()
    else:
        return json_obj

@exam_loader
def from_xml(obj, validate=True, **kwds):
    etree = ElementTree()
    etree.parse(obj)
    json = {}

    # Extract simple properties
    for k, v in schemas.Exam.items():
        if isinstance(v, Str):
            v = etree.find(k)
            if v is not None:
                json[k] = v.text

    # Extract content
    content = []
    for node in (etree.find('content') or []):
        content.append(node.text)
    if content:
        json[u'content'] = content

    # Return validated
    if validate:
        schemas.Exam.validate(json, require_defaults=False)
    return json

if __name__ == '__main__':
    import pprint
    res = from_addr('cálculo 3/módulo 1/lista')
    pprint.pprint(res)
    print(res['content'][0].decode('utf8'))

