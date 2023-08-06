#-*- coding: utf-8 -*-
import functools
from tutor.util import plastex
from tutor.data.conversions.base import Import, Parser, request, push, cooperative
from tutor.config.schemas import NODES


__all__ = [ 'MainImport', 'NamesImport']

#===============================================================================
#                         Importing/Exporting interface
#===============================================================================
class MainImport(Import):
    def load_tex(self, file):
        return TexMainParser(file).parse()

class NamesImport(Import):
    def load_py(self, file):
        return PyNamesParser(file).parse()

    def load_yaml(self, file):
        return YamlNameslParser(file).parse()

    def load_tex(self, file):
        return TexNamesParser(file).parse()
#===============================================================================
#                             LaTeX Main parser
#===============================================================================
class TexMainParser(Parser):
    DEBUG = __name__ == '__main__'

    def __init__(self, file):
        """Convert TeX file representing question to a JSON structure."""

        tex = file.read()
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
        self.tex = '\\usepackage{pytutor} ' + tex

    def parse(self):
        '''
        Parse LaTeX file and build the proper JSON object in the 
        obj.json attribute.
        '''
        self.parsed = plastex.parse(self.tex)
        self.parsed.normalize()
        self.json = { u'content': [] }
        self.queue = []
        self.env = None
        self.parse_main_loop()

        # Delete empty TextNodes 
        content = self.json['content']
        content = [ N for N in content if N.get('text', '_').strip() ]
        self.json['content'] = content
        return self.json

    # Parsing functions --------------------------------------------------------
    TOKENS_WHITELIST = set(['emph'])
    def parse_main_loop(self):
        '''
        Main loop in the parsing of LaTeX document.
        '''
        pre = ''
        token = self.parsed.firstChild

        while token is not None:
            # Check if token is a string of text
            if isinstance(token, basestring):
                data = token.strip()
                token = token.nextSibling
                if data:
                    self.queue.append(data)
                continue

            # Choose parsing method
            if pre:
                method = '%s_%s' % (pre, token.tagName)
            else:
                method = token.tagName
            try:
                if method in self.SIMPLE_JSON_ENTRIES:
                    transform = self.SIMPLE_JSON_ENTRIES[method]
                    method = functools.partial(self.parse_simple_json_entry,
                                               method, transform=transform)
                elif method in self.SIMPLE_ENV_ENTRIES:
                    transform = self.SIMPLE_ENV_ENTRIES[method]
                    method = functools.partial(self.parse_simple_env_entry,
                                               method, transform=transform)
                else:
                    method = getattr(self, 'parse_' + method)
            except AttributeError, ex:
                # Method not found: append data to queue
                if self.DEBUG:
                    if not method in self.TOKENS_WHITELIST:
                        print('unknown tag: %s' % method)
                        print('code: %s' % token.source)
                        raise ex
                self.queue.append(token.source)
                token = token.nextSibling
            else:
                # Execute parsing method
                token, pre = method(token, pre)
                token = token.nextSibling

    # Simple JSON entries ------------------------------------------------------
    SIMPLE_JSON_ENTRIES = {
        'title': None,
        'author': None,
        'date': lambda date: dict(zip([u'day', u'month', u'year'], map(int, date.split('/'))))
    }
    def parse_simple_json_entry(self, name, token, pre='', transform=lambda x: x):
        '''Parser routine for tokens that should be assigned directly to a 
        key in the main JSON dictionary'''
        if not name in self.json:
            data = token.textContent
            if transform is not None:
                data = transform(data)
            self.json[name] = data
        else:
            raise ValueError('trying to reassign entry, %s' % name)
        return token, pre

    # Simple environment entries -----------------------------------------------
    ANSWER_VALUES = { 't': True, 'true': True, 'f': False, 'false': False }
    SIMPLE_ENV_ENTRIES = {
        'answer': lambda x: TexMainParser.ANSWER_VALUES[x.lower()],
        'value': float,
        'feedback': None,
        'comment': None,
        'solution': None,
        'associatewith': None,
    }
    def parse_simple_env_entry(self, name, token, pre='', transform=None):
        '''Parser routine for tokens that should be assigned directly to a 
        key in the local self.env dictionary'''

        # Retrieve source and remove the heading \name{ and trailing }
        data = token.source.strip()
        data = data[len(name) + 2:-1]
        if transform is not None:
            try:
                data = transform(data)
            except:
                print 'TODO: invalid transform: %s=%s' % (name, data)

        if self.env is None:
            print('warning: trying to assign token %s=%s to null env' % (name, data))
            return token, pre

        if not name in self.env:
            self.env[unicode(name)] = data
        else:
            raise ValueError('trying to reassign entry, %s' % name)
        return token, pre

    # Other parser functions ---------------------------------------------------
    def parse_usepackage(self, token, pre=''):
        return token, pre

    def parse_par(self, token, pre=''):
        return token, pre

    def parse_maketitle(self, token, pre=''):
        if self.queue:
            raise RuntimeError('self.queue should be empty, got %s' % self.queue)
        return token, pre

    def parse_introtext(self, token, pre=''):
        text = ''.join(par.source for par in token).strip()
        self.json['content'].append({ u'type': u'text',
                                      u'text': text })
        return token, pre

    def parse_association(self, token, pre=''):
        parser = cooperative(self.parse_env_coroutine(token, pre))
        parser.send('env name', 'association')
        parser.send('item keys', [ u'feedback', u'value', u'comment', u'associatewith' ])
        ret = parser.finish()

        # Make items with \emptyassociation null
        for item in self.json['content'][-1]['items']:
            if '\\emptyassociation' in item['text']:
                item['text'] = None
            item['text_domain'] = item.pop('text', None)
            item['text_image'] = item.pop('associatewith', None)

        return ret

    def parse_multiplechoice(self, token, pre=''):
        parser = cooperative(self.parse_env_coroutine(token, pre))
        parser.send('env name', u'multiple-choice')

        # Add ids in items
        env = parser.get('post-processing')
        for idx, item in enumerate(env['items']):
            item[u'id'] = idx

        return parser.finish()

    def parse_truefalse(self, token, pre=''):
        parser = cooperative(self.parse_env_coroutine(token, pre))
        parser.send('env name', u'true-false')
        parser.send('item keys', [ u'feedback', u'answer', u'comment'])
        return parser.finish()

    # Auxiliary functions ------------------------------------------------------
    def remove_entries(self, tk_list, entries):
        '''
        Remove all tokens with names given in entries and return a tuple
        with the new token list and a dictionary mapping entries to their
        respective values
        '''
        old_env = self.env
        self.env = {}
        try:
            new_list = []
            entries = set(entries)
            for tk in tk_list:
                name = getattr(tk, 'tagName', '_')
                if name in entries:
                    func = self.SIMPLE_ENV_ENTRIES[name]
                    self.parse_simple_env_entry(name, tk, '', func)
                else:
                    new_list.append(tk)
            entries = self.env
        finally:
            self.env = old_env

        return new_list, entries

    def parse_env_coroutine(self, token, pre=''):
        '''
        Co-routine that implements parses multiplechoice/truefalse/association
        nodes. 
        '''

        env = (yield request('env init')) or {}
        name = (yield request('env name')) or ''
        env[u'type'] = unicode(name)

        # Process direct env entries
        key_entries = (yield request('keys')) or ['solution', 'feedback', 'value', 'comment']
        tk_list = (tk for par in token for tk in par)
        tk_list, env_update = self.remove_entries(tk_list, key_entries)

        # Process options
        if token.getAttribute('options'):
            options = token.getAttribute('options').split(',')
            options = map(unicode.strip, options)
            options = [ x.split('=') for x in options ]
            for k, v in options:
                try:
                    env[unicode(k)] = NODES[name][k].from_string(v)
                except KeyError:
                    raise ValueError("unexpected option in '%s' environment: %s" % (name, k))

        # Update environment
        env.update(env_update)
        items = env[u'items'] = []

        # Extract items
        items_tk = None
        for i, tk in list(enumerate(tk_list)):
            name = getattr(tk, 'tagName', '_')
            if name in [ 'items', 'enumerate']:
                del tk_list[i]
                if items_tk is None:
                    items_tk = tk
                else:
                    raise ValueError('duplicated items sections in the same environment')

        # Save stem
        env['stem'] = ''.join([ c.source.strip() for c in tk_list ])

        # Process items
        key_entries = (yield request('item keys')) or [ u'feedback', u'value', u'comment']
        for item in items_tk:
            tokens = (tk for par in item for tk in par)
            tk_list, item = self.remove_entries(tokens, key_entries)
            data = ''.join([ c.source.strip() for c in tk_list ])
            item[u'text'] = self.clean_string(data)
            items.append(item)

        # Post-process env
        yield push('post-processing', env)

        # Clean up and return
        self.json['content'].append(env)
        yield token, pre

    def consume_queue(self, queue=None):
        '''
        Convert queue to string and re-start it
        '''

        if queue is None:
            queue = self.queue
        ret = ' '.join(queue)
        queue[:] = []
        return ret.replace('  ', ' ')

    def clean_string(self, st):
        '''
        Remove heading whitespace and trailing whitespace and \\'s
        '''
        st = st.strip()
        while True:
            if st.endswith(r'\\'):
                st = st[:-2].strip()
            else:
                break
        return st

#===============================================================================
#                          Namespace objects parsers
#===============================================================================
class PyNamesParser(Parser):
    def parse(self):
        data = self.file.read()
        data = data.decode('utf8')
        return { u'type': u'python', u'code': data, u'var_names': [] }

class YamlNameslParser(Parser):
    pass

class TexNamesParser(Parser):
    pass

if __name__ == '__main__':
    from pprint import pprint
    from tutor.data.raw_lib import LibNode

    ln = LibNode('learning_obj', 'examples', 'lyx_simple')
    ln = LibNode('learning_obj', 'cálculo 3', 'integrais múltiplas', 'l4', 'jacobianos')
    loc = MainImport()
    with ln.open('main') as F:
        obj = loc.load(F, 'lyx')
    pprint(obj['content'][-1]['stem'])
