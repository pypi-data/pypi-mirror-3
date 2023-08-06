#-*- coding: utf8 -*-
from cStringIO import StringIO
from tutor.transforms.var_filters import DEFAULT_FILTERS
from tutor.util.jsonlib import all as jsonlib
import os
import random
import sys
import tempfile

class Creator(object):
    def __init__(self, template):
        self.template = template

    def new(self):
        raise NotImplementedError

class LearningObj(Creator):
    def __init__(self, template):
        super(LearningObj, self).__init__(template)
        self.namespace = template.get('namespace_pool', None)
        self.subs = template.get('namespace_subs', None)
        if self.namespace and self.namespace['type'] == 'python':
            # Save code to temporary file
            code = self.namespace['code']
            self._tmp_py_module_file = tempfile.NamedTemporaryFile('w', suffix='.py', prefix='script_module_')
            self._tmp_py_module_file.write(code)
            self._tmp_py_module_file.flush()

            # Save module properties
            tmp_fname = self._tmp_py_module_file.name
            mod_name = os.path.basename(tmp_fname)
            self._mod_name = os.path.splitext(mod_name)[0]
            self._mod_path = os.path.dirname(tmp_fname)

    def _load_mod_vars(self):
        for _ in range(10):
            try:
                mod = self._mod
            except AttributeError:
                cwd = os.getcwd()
                try:
                    sys.path.append(self._mod_path)
                    mod = __import__(self._mod_name)
                    os.chdir(self._mod_path)
                finally:
                    os.chdir(cwd)
                    sys.path.pop()
            else:
                mod = reload(mod)
            return vars(mod)
        else:
            raise RuntimeError('script made 10 consecutive errors, aborting')

    def new(self):
        '''
        Create a new object based on the given template.
        '''
        reps = 10
        while reps > 0:
            reps -= 1
            child = jsonlib.copy(self.template)

            # Execute code
            if self.namespace is not None:
#                print 'Question: %s --- %s' % (self.template['name'], self.template['title'])
                worker = getattr(self, 'ns_' + self.namespace['type'])
                vars = worker(child)
                subs = jsonlib.compute_subs(self.subs, vars, DEFAULT_FILTERS)
                jsonlib.jpath_update(child, subs)

            # Update nodes
            for idx, node in enumerate(child['content']):
                node_type = node['type'].replace('-', '_')
                new_node = getattr(self, 'new_%s' % node_type, self.new_generic)
                try:
                    child['content'][idx] = new_node(node, idx)
                except ValueError:
                    continue

            # Clean-up operations
            if 'namespace_pool' in child:
                del child['namespace_pool']
                del child['namespace_subs']
        return child

    def new_multiple_choice(self, node, idx=None):
        # Assert that there are no repeated answers
        values = jsonlib.jpath(node, '$.items.*.text')
        values_set = set(values)
        if len(values) != len(values_set):
            for value in values:
                if value in values_set:
                    values_set.remove(value)
                else:
                    reps = []
                    for (p, v) in jsonlib.walk(node['items']):
                        if p.endswith('text') and v == value:
                            reps.append(p.split('.')[1])
                    reps = ','.join(reps)
                    msg = '%s: ' % self.template['name']
                    msg += "repeated values at '$.content.%s.items.[%s].text': %s" % (idx, reps, value)
                    raise ValueError(msg)

        # Randomize content
        if node.get('shuffle', True):
            random.shuffle(node['items'])

        return node

    def new_generic(self, node, idx=None):
        return node

    def new_association(self, node, idx=None):
        idx_list = [ i for (i, v) in enumerate(node['items']) if v['text_image'] ]
        node['image_ordering'] = idx_list
        if node.get('shuffle', True):
            random.shuffle(idx_list)
        node['image_ordering'] = idx_list
        return node

    def ns_python(self, obj, ntries=10):
        stdold = sys.stderr, sys.stdout
        stdtmp = StringIO()
        sys.stderr = sys.stdout = stdtmp

#        namespace_dic = self._load_mod_vars()
        try:
            namespace_dic = self._load_mod_vars()
        except Exception as ex:
            stdold[1].write(stdtmp.getvalue())
            raise ex
        finally:
            sys.stderr, sys.stdout = stdold

        return dict((name, namespace_dic.get(name, '')) for name in self.namespace['var_names'])

class Exam(Creator):
    def __init__(self, template):
        super(Exam, self).__init__(template)
        self.content = template.get('content', [])
        self.creators = [ LearningObj(lobj) for lobj in self.content ]

    def new(self):
        '''
        Create a new object based on the given template.
        '''

        child = jsonlib.copy(self.template)
        child['content'] = [ C.new() for C in self.creators ]

        return child

    def ns_python(self, obj, ntries=10):
        stdold = sys.stderr, sys.stdout
        stdtmp = StringIO()
        try:
            sys.stderr = sys.stdout = stdtmp
            namespace_dic = {}
            code = self.namespace['code'].strip()
            if code.startswith('#-*-'):
                code = '\n'.join(code.splitlines()[1:])
            try:
                exec code in namespace_dic
            except Exception as ex:
                stdold[1].write(stdtmp.getvalue())
                raise ex
        except AssertionError as ex:
            if ntries > 0:
                return self(ntries - 1)
            else:
                raise ex
        finally:
            sys.stderr, sys.stdout = stdold

        return dict((name, namespace_dic.get(name, '')) for name in self.namespace['var_names'])

def new_learning_obj(template, size=None):
    '''
    Create a new Learning Object based on 'template'. If size is given, returns
    a list of 'size' different Learning Objects.
    '''

    if size is None:
        return LearningObj(template).new()
    else:
        tmpl = LearningObj(template)
        return [ tmpl.new() for _ in range(size) ]

def new_exam(template, size=None):
    '''
    Create a new Exam based on 'template'. If size is given, returns  a list of
    'size' different objects.-
    '''

    if size is None:
        return Exam(template).new()
    else:
        tmpl = Exam(template)
        return [ tmpl.new() for _ in range(size) ]

if __name__ == '__main__':
    from pprint import pprint
    from tutor.data import tutor_lib as lib
    from chips import debug

    with debug.printtime():
        #tmpl = lib.get_learning_obj('examples/namespace')
        tmpl = lib.get_learning_obj('cálculo 3/m6/teorema de gauss 2')
#        tmpl = lib.get_exam('examples/lyx_simple')
        new = new_learning_obj(tmpl, 2)
    pprint(new)
