from tutor import convert
from tutor.config import settings
import os

def load_json(name):
    """Loads JSON structure associated to 'name' from shared questions 
    database"""

    filename = get_filename(name)
    _, __, ext = filename.partition(name)
    ext = ext.split('.')

    # load basic json structure
    with open(filename, 'r') as F:
        json = getattr(convert, 'from_' + ext[-1])(F)
        script = ''
        language = 'python'

    # load script of mixed file formats: only python is currently supported
    if ext[-2] == 'view':
        ext_len = sum(map(len, ext)) + len(ext) - 1
        src_file = filename[:-ext_len] + '.py'
        with open(src_file) as F:
            script = F.read()

    # normalize json
    return json

def get_filename(name):
    """Get filename associated with a given 'name' in the shared questions 
    database."""

    # determine if address correspond to a latex file, a python file or 
    # is of mixed type and call the relevant methodname
    base = settings.TEMPLATE_LEARNING_OBJ_PATH
    path = os.path.join(base, name)

    # load in order of preference
    for ext in [ 'view.lyx', 'view.tex', 'view.xml', 'lyx', 'tex', 'xml', 'json', 'py']:
        filename = '%s.%s' % (path, ext)
        if os.path.exists(filename):
            return filename

    # if no file is found...
    raise ValueError("not found, '%s.*'!" % base)

def get_mtime(name):
    """Get modification time for 'name' in the shared questions database."""

    fname = get_filename(name)
    return os.path.getmtime(fname)

if __name__ == '__main__':
    import pprint
    addr = 'exemplos/demolyx'
    #addr = 'c3/integrais_linha/helicoidal'
    pprint.pprint(load_json(addr))
