#-*- coding: utf-8 -*-
import os
import re
from pprint import pprint
from tutor.util import plastex, jsonlib
from tutor.config import schemas
from tutor.lib import Addr

DEBUG = __name__ == '__main__'
#===============================================================================
#                 Mapping: type -> from_...() functions
#===============================================================================
LOADERS = {}
def loader(func):
    ext = func.func_name.split('_')[1]
    LOADERS[ext] = func
    return func

#===============================================================================
#                 Mapping: type -> from_...() functions
#===============================================================================
POOL_LOADER = {}
def pool_loader(func):
    ext = func.func_name.split('_')[1]
    POOL_LOADER[ext] = func
    return func

#===============================================================================
#                                Pool loader
#===============================================================================
@pool_loader
def pool_py(file):
    data = file.read()
    data = data.decode('utf8')
    return { u'type': u'python', u'code': data }

def from_view(json, validate=True, **kwds):
    # Build name substitutions
    subs = jsonlib.get_subs(json, braces=('||', '||'),
                            escape=(r'\||', r'\||'),
                            filter_fmt=jsonlib.filter_fmt_math)

    # Convert these substitutions to use the right Schema
    namesubs = []
    for path, (text, vars) in subs.items():
        vars = [ {u'var_name': var[0], u'filters': var[1:]} for var in vars ]
        sub = { u'path': path,
                u'text': text,
                u'substitutions': vars }
        namesubs.append(sub)
    json[u'namespace_subs'] = namesubs

    if validate:
        LearningObj.validate(json, use_opt=True)
    return json

def from_addr(addr, validate=True, ret_modified=False, **kwds):
    # Import the JSON structure from the template's view
    addr_path = addr
    addr = Addr(addr, base='learning_obj')
    if not addr.exists():
        raise IOError('invalid address %s' % addr_path)
    view = addr.get_data()
    loader = LOADERS[addr.get_data_type()]
    json_obj = loader(view, validate=False, **kwds)

    # Import name pool, if necessary 
    if addr.has_aux():
        # Create names_subs
        json_obj = from_view(json_obj, validate=False)
        names = jsonlib.jpath(json_obj, '$.namespace_subs.*.substitutions.*.var_name')
        names = list(set(names))

        # Create names_pool
        pool_type, pool = addr.get_main_aux()
        pool = POOL_LOADER[pool_type](pool)
        pool['names'] = names
        json_obj['namespace_pool'] = pool

    # Save creation time
    dt = addr.get_mtime()
    keys = [u'day', u'month', u'year', u'hour', u'minute', u'second', u'microsecond']
    json_obj[u'name'] = addr_path
    json_obj.setdefault(u'is_template', True)
    json_obj.setdefault(u'template_name', addr_path)
    json_obj.setdefault(u'parent', None)

    # Build file_list, if necessary
    if validate:
        schemas.LearningObj.validate(json_obj)
    if ret_modified:
        return json_obj, dt
    else:
        return json_obj

@loader
def from_lyx(lyx, validate=True, **kwds):
    """Convert TeX file representing question to a JSON structure."""

    try:
        lyx = lyx.name
    except:
        pass

    cmd = 'lyx -f -e latex "%s"' % lyx
    try:
        # convert using LyX in the command-line
        os.system(cmd)
        tex = lyx[:-3] + 'tex'

        # load json from tex file
        json = from_tex(tex, validate)
    finally:
        # delete tex and lyx~ files
        os.remove(tex)
        try:
            os.remove(lyx + '~')
        except OSError:
            pass

    return json

@loader
def from_tex(tex, validate=True, **kwds):
    """Convert TeX file representing question to a JSON structure."""

    # if XML is a string, creates a file object 
    if isinstance(tex, basestring):
        with open(tex, 'r') as F:
            tex = F.read()
    else:
        tex = tex.read()

    # find the right encoding
    try:
        pre = tex[:tex.index('{inputenc}')]
        _, __, encoding = pre.rpartition('\usepackage')
        encoding = encoding.strip('[]')
    except ValueError:
        encoding = 'utf8'
    tex = tex.decode(encoding)

    # Bug in plasTeX misses a closing braket in commands such as \cmd {}
    # if cmd is not known to plasTeX.
    tex = tex.replace('{}', '{ }')

    # Preamble does not matter to us.
    __, _, tex = tex.partition('\\begin{document}')
    tex, _, __ = tex.rpartition('\\end{document}')

    # Transform to json
    json = TeXConverter(tex).json

    # Validate and return.
    if validate:
        schemas.LearningObj.validate(json, True)
    return json

#------------------------------------------------------------------------------
#    Class that extract features
#------------------------------------------------------------------------------
class TeXConverter(object):
    def __init__(self, tex):
        self.parsed = plastex.parse(tex)
        self.parsed.normalize()
        self.json = { u'content': [] }
        self.queue = []
        self.env = None
        self.parse(self.parsed.firstChild)

        # Delete empty TextNodes 
        content = self.json['content']
        content = [ N for N in content if N.get('text', 'foo').strip() ]
        self.json['content'] = content

    # Parsing functions --------------------------------------------------------
    def parse(self, token, pre=''):
        if isinstance(token, basestring):
            if token.strip():
                self.queue.append(token)
        elif token is None:
            return
        else:
            if pre:
                method = 'parse_%s_%s' % (pre, token.tagName)
            else:
                method = 'parse_' + token.tagName
            try:
                method = getattr(self, method)
            except AttributeError, ex:
                if DEBUG:
                    mname = method[len('parse_'):]
                    if not mname in ('emph', 'math', '\\',
                                     'multiplechoice_math', 'align*'
                                     'multiplechoice_\\', 'textbf',
                                     'multiplechoice_emph', 'displaymath',
                                     'bgroup', 'grade', 'align*'
                                     'active::~'):
                        print('unknown tag: %s' % method)
                        print('code: %s' % token.source)
                        raise ex
                self.queue.append(token.source)
                return self.parse(token.nextSibling, pre)
            token = method(token, pre)

        self.parse(token.nextSibling, pre)

    def parse_par(self, token, pre=''):
        return token

    def parse_title(self, token, pre=''):
        self.json[u'title'] = token.textContent
        return token

    def parse_author(self, token, pre=''):
        self.json[u'author'] = token.textContent
        return token

    def parse_date(self, token, pre=''):
        dmy = token.textContent.split('/')
        d, m, y = map(int, dmy)
        self.json[u'date'] = { u'day': d, u'month': m, u'year': y }
        return token

    def parse_maketitle(self, token, pre=''):
        if self.queue:
            raise RuntimeError('self.queue should be empty, got %s' % self.queue)
        self.env = { u'type': u'text' }
        return token

    OPTION_TRANSLATIONS = { 'true': True, 'false': False }
    def parse_option(self, token, pre=''):
        option_tk = token.nextSibling
        value_tk = option_tk.nextSibling

        # Compute value
        value = value_tk[0]
        try:
            value = int(value)
        except ValueError:
            try:
                value = float(value)
            except ValueError:
                value = self.OPTION_TRANSLATIONS.get(value.lower(), value)

        # Save in environment
        option = option_tk[0].replace('-', '_').replace(' ', '_')
        self.env[option] = value
        return value_tk

    def parse_multiplechoice(self, token, pre=''):
        self.process_env()
        self.env = { u'type': u'multiple-choice',
                     u'items': []}
        token, grade = self.process_grade(token)
        if not grade is None:
            self.env[u'grade'] = grade
        return token

    def parse_association(self, token, pre=''):
        self.process_env()
        self.env = { u'type': u'association',
                     u'items': []}
        token, grade = self.process_grade(token)
        if not grade is None:
            self.env[u'grade'] = grade
        return token

    def parse_truefalse(self, token, pre=''):
        self.process_env()
        self.env = { u'type': u'true-false',
                     u'items': []}
        token, grade = self.process_grade(token)
        if not grade is None:
            self.env[u'grade'] = grade
        return token

    def parse_enumerate(self, token, pre=''):
        self.queue.append(token)
        self.process_env()
        return token

    # Environments -------------------------------------------------------------
    def env_text(self):
        node = { u'type': u'text',
                 u'text': self.clean_string(self.consume_queue()) }
        self.json['content'].append(node)
        self.env = None

    def env_multiplechoice(self):
        enum = self.queue.pop()
        self.json['content'].append(self.env)

        # save stem
        self.env[u'stem'] = self.clean_string(self.consume_queue())

        # process environment items
        for i, item in enumerate(enum.childNodes):
            item = item.source
            item = self.process_multiplechoice_item(item)
            item['id'] = i
            self.env['items'].append(item)

        # check if there is a non-null grade
        if all(map(lambda x: x['grade'] == 0, self.env['items'])):
            self.env['items'][0][u'grade'] = 1
        self.env = None

    def process_multiplechoice_item(self, src):
        text, _, others = src.partition('\\feedback')
        if '\\comment' in text:
            text, _, comment = src.partition('\\comment')
        else:
            feedback, _, comment = others.partition('\\comment')

        # format strings
        text = text[len('\\item'):].strip()
        feedback = feedback.strip()
        comment = comment.strip()

        # extract grade from 'text'
        if text.startswith('\\grade'):
            _, __, text = text.partition('{')
            grade, _, text = text.partition('}')
            try:
                grade = float(grade.strip())
            except ValueError:
                grade = grade.strip()
        else:
            grade = 0

        C = self.clean_string
        ret = { u'grade': grade, u'text': C(text) }
        if feedback:
            ret[u'feedback'] = C(feedback)
        if comment:
            ret[u'comment'] = C(comment)
        return ret

    def env_truefalse(self):
        enum = self.queue.pop()
        self.json['content'].append(self.env)

        # save stem
        self.env[u'stem'] = self.clean_string(self.consume_queue())

        # process environment items
        for item in enum.childNodes:
            # create item
            item = item.source
            item = self.process_truefalse_item(item)
            self.env['items'].append(item)

        self.env = None

    def process_truefalse_item(self, src):
        # \feedback before \comment
        text, _, others = src.partition('\\feedback')
        if '\\comment' in text:
            text, _, comment = src.partition('\\comment')
        else:
            feedback, _, comment = others.partition('\\comment')

        # format strings
        C = self.clean_string
        text = text[len('\\item'):].strip()
        feedback = feedback
        comment = comment

        # extract grade from 'text'
        if text.startswith('\\answer'):
            _, __, text = text.partition('{')
            value, _, text = text.partition('}')
            value = { 't': True, 'f': False }[value.strip().lower()]
        else:
            raise ValueError("\\answer tag not found: '%s'" % text)

        ret = {u'answer': value,
               u'text': C(text) }
        if comment:
            ret[u'comment'] = C(comment)
        if feedback:
            ret[u'feedback'] = C(feedback)
        return ret

    def env_association(self):
        enum = self.queue.pop()
        self.json['content'].append(self.env)

        # save stem
        self.env[u'stem'] = self.clean_string(self.consume_queue())

        # process environment items
        for item in enum.childNodes:
            item = self.process_association_item(item)
            self.env['items'].append(item)

        self.env = None

    def process_association_item(self, item):
        keys = [ u'text', u'linksto', u'feedback', u'comment' ]
        values = self.sort_item(item, *keys[1:])
        values = map(self.clean_string, values)
        ret = dict((k, v) for (k, v) in zip(keys, values) if v)
        if 'linksto' in ret:
            ret['answer'] = ret.pop('linksto')
        return ret

    # Auxiliary functions ------------------------------------------------------
    def process_env(self):
        if self.env:
            getattr(self, ('env_' + self.env['type']).replace('-', ''))()

    def consume_queue(self, queue=None):
        if queue is None:
            queue = self.queue
        ret = ' '.join(queue)
        queue[:] = []
        return ret.replace('  ', ' ')

    def process_grade(self, token, default=None):
        if token.tagName == 'grade':
            token = token.nextSibling
            return (token.nextSibling, float(token.textContent))
        elif getattr(token.nextSibling, 'tagName', None) == 'grade':
            token = token.nextSibling.nextSibling
            grade = float(token.textContent)
            return (token, grade)
        else:
            return (token, default)

    def clean_string(self, st):
        st = st.strip()
        if st.endswith(r'\\'):
            st = st[:-2].strip()
        return st

    def sort_item(self, item, *args):
        src = '\\body_text ' + item.source[5:].strip()
        argsset = set('\\%s' % arg for arg in args)
        argsset.add('\\body_text')
        content = {}

        while argsset:
            partitions = []
            for arg in list(argsset):
                partitions.append([arg, src.rpartition(arg)])
            partitions.sort(key=lambda x: len(x[1][2]))
            arg, (src, _, data) = partitions[0]
            content[unicode(arg[1:])] = data.strip()
            argsset.remove(arg)

        # Return answers in the order asked by the user
        ret_value = [ content.pop('body_text') ]
        for arg in args:
            ret_value.append(content[arg])
        return ret_value

#------------------------------------------------------------------------------
if __name__ == '__main__':
    import pprint
#    res = from_addr('examples/lyx_simple', validate=False)
    res = from_addr('cálculo 3/derivadas parciais/derivada direcional/fixação', validate=False)
    pprint.pprint(res)

    print '\n\nChecking validity...'
    schemas.LearningObj.validate(res)
    print 'OK'
