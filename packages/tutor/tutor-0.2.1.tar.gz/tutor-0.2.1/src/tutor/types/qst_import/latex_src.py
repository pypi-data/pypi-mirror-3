#-*- coding: utf-8 -*-
import os
import datetime
from fs.opener import fsopen
from tutor import plastex
from tutor.latex.commands import lyxtotex
from tutor.types.subquestions import (MultipleChoice, MultipleChoiceItem, IntroText)

DEBUG = __name__ == '__main__'

def load_main_lyx(lyx):
    """Convert LyX file representing question to a JSON structure.
    
    If ``lyx`` is a string, it is interpreted as an URI to the .lyx file.
    """
    if isinstance(lyx, basestring):
        with open(lyx) as F:
            return load_main_tex(lyxtotex(F))
    else:
        return load_main_tex(lyxtotex(lyx))

def load_main_tex(tex):
    """Convert TeX file representing question to a JSON structure.
    
    If ``tex`` is a string, it is interpreted as an URI to the .tex file.
    """

    # read tex data
    if isinstance(tex, basestring):
        with fsopen(tex, 'r') as F:
            tex = F.read()
    else:
        tex = tex.read()

    # discover the right encoding
    try:
        inputenc_pos = tex.index('{inputenc}')
        head = tex[:inputenc_pos]
        tail = tex[inputenc_pos:]
    except ValueError:
        encoding = 'ascii'
    else:
        head, usepackage, encoding = head.rpartition('\\usepackage')
        encoding = encoding.strip('[]')
        tex = ''.join([head, usepackage, '[utf8]', tail])
    tex = tex.decode(encoding)
    if '\\value' in tex:
        print 'Warning: A \\value{x} command was found in document, is that right?'

    # Bug in plasTeX misses a closing braket in commands such as \cmd {}
    # if cmd is not known to plasTeX.
    tex = tex.replace('{}', ' ')

    result = TeXConverter(tex, encoding).get_result()

    # Remove inputenc and pytutor packages
    packages = []
    preamble = result['preamble']
    for _, item in enumerate(preamble['packages']):
        if item['name'] not in ['pytutor', 'inputenc', 'fontenc']:
            packages.append(item)
    result[u'preamble'][u'packages'] = packages

    # Change contents of body
    return result

#------------------------------------------------------------------------------
#    Class that extract features
#------------------------------------------------------------------------------
safe_tags = set('''texttt textbf math LaTeX TeX displaymath emph bgroup int
\\ active::~ textcolor'''.split())

class TeXConverter(object):
    def __init__(self, tex, encoding):
        '''Simple LaTeX parser for questions. The constructor extracts the latex
        structure and convert it to its JSON representation.'''

        if not isinstance(tex, unicode):
            raise TypeError("'tex' must be unicode, got %s" % type(tex))

        self._parsed = plastex.parse(tex)
        self._parsed.normalize()
        self._text_queue = []
        self._token_queue = []

        # Create body nodes
        self.root = {}
        self.body = []
        self.preamble = {'packages': []}

        # Main parse loop
        token = self._parsed[0]
        while token is not None:
            token = self.parse(token)
            if token is None:
                try:
                    token = self._token_queue.pop()
                except IndexError:
                    pass

    def push_token(self, token):
        if token is not None:
            self._token_queue.append(token)

    def set_and_clean(self, attr, value):
        '''set value from temporary attribute and clean afterwards'''

        if hasattr(self, '_' + attr):
            raise RuntimeError('assigning to existing attribute: %s' % attr)
        setattr(self, '_' + attr, value)

    def get_and_clean(self, attr, default=None):
        '''get value from temporary attribute and clean afterwards'''

        attr = '_' + attr
        value = getattr(self, attr, default)
        if hasattr(self, attr):
            delattr(self, attr)
        return value

    def get_result(self):
        '''Return the root and body sections to be used by question loader.'''

        dic = vars(self)
        good_keys = set(['root', 'body', 'preamble'])
        for k in dic.keys():
            if k not in good_keys:
                del dic[k]
        return dic

    def make_first_pass(self, token):
        '''
        Implement 2-way parsing.
        
        These parsers must be implemented as::
        
          def parse_...(self, token):
              if self.make_first_pass(token):
                  (do something)
                  return token[0]
              else:
                  (do something else)
                  return token.nextSibling
        '''
        # decide if it is 1st pass or not
        if self._token_queue:
            is_first = self._token_queue[-1] is not token
        else:
            is_first = True

        # Prepare environment for 1st pass
        if is_first:
            # mark token queue for a 2nd pass
            self.push_token(token)
            self.push_token(token)

            # configure environment modifiers
            if token.tagName != 'item':
                self._parse_item = getattr(self, 'process_item_' + token.tagName)

        # Clean environment after 2nd pass
        else:
            self._token_queue.pop()
            if token.tagName != 'item':
                del self._parse_item

        return is_first

    #===========================================================================
    # Parsing functions
    #===========================================================================
    def parse(self, token):
        '''Main parser: dispatch for sub-parsers or parse simple textual 
        content'''

        if isinstance(token, basestring):
            if token.strip():
                self._text_queue.append(token)
            return token.nextSibling

        elif token is None:
            return None

        else:
            method_name = 'parse_' + token.tagName

            try:
                method = getattr(self, method_name)
            except AttributeError as ex:
                if method_name[6:] in safe_tags:
                    self._text_queue.append(token.source)
                    method = lambda x: x.nextSibling
                else:
                    raise ex
            return method(token)

    def parse_documentclass(self, token):
        self.preamble[u'documentclass'] = token.getAttribute('name')
        self.preamble[u'options'] = token.getAttribute('options')
        return token.nextSibling

    def parse_usepackage(self, token):
        name = token.getAttribute('names')
        if len(name) != 1:
            raise ValueError('||usepackage with multiple packages is not suppoted')
        name = name[0]

        options = token.getAttribute('options')
        if options is None:
            options = {}

        package = {u'name': name, u'options': options}
        self.preamble['packages'].append(package)
        return token.nextSibling

    def parse_makeatletter(self, token):
        return token.nextSibling

    def parse_makeatother(self, token):
        return token.nextSibling

    def parse_document(self, token):
        self._text_queue = []
        return token[0]

    def parse_par(self, token):
        if not list(token):
            self._text_queue.append('\n\n')
            return token.nextSibling
        else:
            self.push_token(token.nextSibling)
            return token[0]

    def parse_title(self, token):
        self.root[u'title'] = token.textContent.strip()
        return token.nextSibling

    def parse_author(self, token):
        self.root[u'author'] = token.textContent.strip()
        return token.nextSibling

    def parse_date(self, token):
        if '/' in token.textContent:
            dmy = token.textContent.split('/')
            d, m, y = map(int, dmy)
            new = datetime.datetime(y, m, d)
        else:
            date, time = token.textContent.split(' ')
            y, m, d = map(int, date.split('-'))
            h, mm, s = time.split(':')
            s, ms = s.split('.')
            h, mm, s, ms = map(int, [h, mm, s, ms])
            new = datetime.datetime(y, m, d, h, mm, s)

        self.root[u'ctime'] = new
        return token.nextSibling

    def parse_maketitle(self, token):
        if self._text_queue:
            raise RuntimeError('self._text_queue should be empty, got % s' % self._text_queue)
        self._env = { u'type': u'text' }
        return token.nextSibling

    def parse_enumerate(self, token):
        self.push_token(token.nextSibling)
        self._text = self.consume_queue()
        self._items = []
        if list(token):
            return token[0]
        else:
            return token.nextSibling

    def parse_item(self, token):
        if self.make_first_pass(token):
            return token[0]
        else:
            pre_node = {}
            value, feedback, comment = map(self.get_and_clean, ['value', 'feedback', 'comment'])
            if value is not None:
                pre_node[u'value'] = value
            if feedback is not None:
                pre_node[u'feedback'] = feedback
            if comment is not None:
                pre_node[u'comment'] = comment

            pre_node[u'text'] = self.clean_string(self.consume_queue())
            self._items.append(self._parse_item(token, pre_node))
            return token.nextSibling

    def parse_grade(self, token):
        value = token.getAttribute('text').source
        self.set_and_clean('value', value)
        return token.nextSibling

    def parse_value(self, token):
        raise DeprecationWarning('\\value{x} is deprecated in favor of \\grade{x}')

    def parse_feedback(self, token):
        value = token.getAttribute('text').source
        self.set_and_clean('feedback', value)
        return token.nextSibling

    #===========================================================================
    # Environments
    #===========================================================================
    def parse_introtext(self, token):
        pars = [ getattr(c, 'source', str(c)) for c in token ]
        text = self.clean_string(''.join(pars))
        intro = IntroText(text=text)
        intro.adapt(inplace=True, force=True)
        self.body.append(intro)
        return token.nextSibling

    def parse_multiplechoice(self, token):
        if self.make_first_pass(token):
            return token[0]
        else:
            options = token.getAttribute('options')
            if options is not None:
                schema = MultipleChoice.schema
                opts = {}
                options = (o.split('=') for o in options.split(','))
                options = { k.strip(): v.strip() for (k, v) in options }

                # Save adapted valid keys
                for k in options.keys():
                    try:
                        opts[k] = schema[k].adapt(options[k], force=True)
                    except KeyError:
                        pass
                    else:
                        options.pop(k)

                # Save post-conversions
                setters = {}
                for k in options.keys():
                    if k.startswith('set:'):
                        setters[k[4:]] = options.pop(k)
                opts['post_process'] = setters

                if options:
                    k, _ = options.popitem()
                    raise ValueError('unrecognized option in multiple-choice environment: %s' % k)

            else:
                opts = {}

            stem = self.clean_string(self._text)
            items = [ MultipleChoiceItem.from_data(x) for x in self._items ]
            node = MultipleChoice(stem=stem)
            node.dictview.update(opts)
            node.adapt(inplace=True, force=True)
            node.items = items
            self.body.append(node)
            return token.nextSibling

    def process_item_multiplechoice(self, item, node=None):
        node = {} if node is None else node
        return node

    #===========================================================================
    # Auxiliary functions
    #===========================================================================
    OPTION_TRANSLATIONS = { 'true': True, 'false': False }
    def format_options(self, token):
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
        option = option_tk[0].replace(' - ', '_').replace(' ', '_')
        self._env[option] = value
        return value_tk

    def consume_queue(self, queue=None):
        if queue is None:
            queue = self._text_queue
        ret = ''.join(queue)
        queue[:] = []
        return ret.replace('  ', ' ')

    def clean_string(self, st):
        st = st.strip()
        if st.endswith(r'\\'):
            st = st[:-2].strip()
        return st

if __name__ == '__main__':
    import pyson
    from tutor.types.question import QuestionPool
    q = QuestionPool('foo', title='My Question', author='Someone')
    t = q.src.open_main()
    obj = load_main_tex(t)['body'][0]
    obj.adapt(inplace=True)
    pyson.pprint(dict(obj.dictview))
    import doctest
    doctest.testmod(optionflags=doctest.REPORT_ONLY_FIRST_FAILURE, verbose=0)
