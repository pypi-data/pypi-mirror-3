#-*- coding: utf8 -*-
from tutor.config import schemas
import collections
import functools
import os
import string
import sys
import types


#===============================================================================
#                                  Constants
#===============================================================================

# Special answer types
class Answer(object):
    def __init__(self, answer=None):
        self.answer = answer

    def to_dict(self):
        return { u'type': unicode(type(self).__name__.lower()), u'answer': unicode(self.answer) }

class INVALID(Answer):
    pass

class NOT_MARKED(INVALID):
    def __init__(self, answer=None):
        super(NOT_MARKED, self).__init__(answer)

    def to_dict(self):
        return None

class VALID(Answer):
    def __init__(self, answer=None, value_pc=None):
        super(VALID, self).__init__(answer)
        self.value_pc = value_pc

    def to_dict(self):
        return { u'type': u'manual', u'answer': unicode(self.answer),
                 u'value_pc': float(self.value_pc) }

class CORRECT(VALID):
    def __init__(self, answer=None):
        super(CORRECT, self).__init__(answer, 100.0)

class INCORRECT(VALID):
    def __init__(self, answer=None):
        super(INCORRECT, self).__init__(answer, 0.0)

# Module constants
LETTERS = set(string.ascii_lowercase)

class Static(object):
    pass

#===============================================================================
#                         Basic JSON Transformations
#===============================================================================

# Implements a Mapping
class _Delegate(collections.MutableMapping):
    def __init__(self, obj):
        self._json = obj

    def __getitem__(self, key):
        return self._json[key]

    def __setitem__(self, key, value):
        self._json[key] = value

    def __delitem__(self, key):
        del self._json[key]

    def __iter__(self):
        return iter(self._json)

    def __len__(self):
        return len(self._json)

_aux = ((k, getattr(_Delegate, k)) for k in dir(_Delegate))
_aux = ((k, v) for (k, v) in _aux if not k.startswith('_abc'))
_aux = ((k, v.im_func) for (k, v) in _aux if hasattr(v, 'im_func'))
_dict = dict(_aux)
JSONDelegate = type('JSONDelegate', (object,), _dict)

class JSONTransforms(JSONDelegate):
    SCHEMA = NotImplemented

    class __metaclass__(type):
        def __new__(cls, name, bases, dict):
            # Creates new class
            new = type.__new__(cls, name, bases, dict)

            # Make static API
            new.static = Static()
            new._instance = new({}, validate=False)
            for method_name in dir(new):
                method = getattr(new, method_name)
                if (not method_name.startswith('_')) and isinstance(method, collections.Callable):
                    new_method = functools.partial(cls.wrapped_method_call, new, method_name)
                    setattr(new.static, method_name, new_method)

            # Create module and put it in sys.modules
            new.module = types.ModuleType(dict.get('MODULE_NAME', name))
            for k, v in vars(new.static).items():
                if not k.startswith('_'):
                    setattr(new.module, k, v)

            sys.modules['%s.%s' % (new.__module__, name)] = new.module
            return new

        @staticmethod
        def wrapped_method_call(cls, method_name, obj, *args, **kwds):
            cls._instance._replace_json(obj)
            old_method = getattr(cls._instance, method_name)
            return old_method(*args, **kwds)

    def __init__(self, obj, validate=True):
        if validate:
            pass
#            self.SCHEMA.validate(obj)
        JSONDelegate.__init__(self, obj)

    def _replace_json(self, obj):
        '''
        Internal use: take all actions to replace the self._json object by 
        a different JSON structure in 'obj'.
        '''
        self._json = obj

#===============================================================================
#                                  Grading
#===============================================================================
class HasGrades(JSONTransforms):
    def grade(self, silent=True):
        raise NotImplementedError

    def value(self):
        return self._json.get('value', 1.0)

    # Interactive responses ----------------------------------------------------
    def iresponse_convert(self, ans):
        raise NotImplementedError

    def iresponse_read(self, buffer):
        # Disregard whitespace        
        whitespace = set(' \n;')
        while buffer and buffer[0] in whitespace:
            buffer = buffer[1:]

        # Prevents reading from empty buffer
        if not buffer:
            raise ValueError('empty buffer')

        if buffer[0] in self.iresponse_char_feed():
            return (buffer[0], buffer[1:])
        else:
            ans, _, buffer = buffer.partition(';')
            ans = ans.strip()
            if self.iresponse_valid_syntax(ans):
                return ans, buffer
            else:
                raise ValueError('invalid answer: %s' % ans)

    def iresponse_char_feed(self):
        raise NotImplementedError

    def iresponse_valid_syntax(self, ans):
        raise NotImplementedError

    def iresponse_right(self, short=True):
        raise NotImplementedError

    def iresponse_complete(self, ans):
        raise NotImplementedError

#===============================================================================
#                             Items manipulation
#===============================================================================
class HasItems(JSONTransforms):
    def subitems(self):
        return iter(self._json.get('items', []))

    def subitems_values(self):
        return iter([ item.get('value', 0.0) for item in self.subitems() ])

    def subitems_value_max(self):
        max_value = max(self.subitems_values())
        if max_value == 0:
            import pprint
            pprint.pprint(self._json)
            raise ValueError('invalid itemized object: all values are null')
        else:
            return max_value

    def subitems_right(self):
        #TODO: support multiple correct items...
        items_list = list(self.subitems())
        items_list.sort(key=lambda x: x.get('value'), reverse=True)
        return [ items_list[0] ]

#===============================================================================
#                            Content manipulation
#===============================================================================
class HasContent(JSONTransforms):
    CONTENT_TYPES = {}

    def content(self):
        return iter(self._json.get('content', []))

    def content_objects(self):
        for obj in self.content():
            try:
                item_type = self.CONTENT_TYPES[obj.get('type', None)]
            except KeyError:
                raise ValueError('invalid sub-object type: %s' % obj.get('type', '<unknown type>'))
            else:
                yield item_type(obj)

class Node(JSONTransforms):
    SCHEMA = schemas.Node

#===============================================================================
#                         Multiple Choice questions
#===============================================================================
class MultipleChoice(Node, HasGrades, HasItems):
    SCHEMA = schemas.MultipleChoice
    ITEMS_SCHEMA = schemas.MultipleChoiceItem
    EXAMPLE = { 'type': 'multiple-choice',
                'stem': 'Mark the answer to the ultimate question',
                'items': [
                    { 'value': 0, 'text': '12', 'id': 1 },
                    { 'value': 1, 'text': '42', 'id': 0 },
                    { 'value': 0, 'text': '10', 'id': 2 }, ], }

    # Auxiliary ----------------------------------------------------------------
    def id_index(self, id):
        for idx, item in enumerate(self.subitems()):
            if item['id'] == id:
                return idx
        else:
            raise ValueError('invalid id: %s' % id)

    # Grading ------------------------------------------------------------------
    def grade(self, silent=True):
        'Compute the grade of multiple-choice object'

        try:
            response = self._json['response']
        except KeyError:
            return 0.0
        else:
            # Find the 'value' attribute of item with given 'id'
            if isinstance(response, int):
                try:
                    idx = self.id_index(response)
                except ValueError as ex:
                    if silent:
                        value = 0.0
                    else:
                        raise ex
                else:
                    value = self._json['items'][idx].get('value', 0.0)

                return self.value() * (value / self.subitems_value_max())

            # Process an special response
            else:
                if response['type'] == 'manual':
                    return self.value() * response.get('value_pc', 0.0) / 100.0
                if response['type'] == 'invalid':
                    if silent:
                        return 0.0
                    else:
                        raise ValueError('invalid answer: %s' % response.get('answer', '<empty>'))

    # Interactive responses ----------------------------------------------------
    _ORD_A = ord('a')
    _CHAR_FEED = set(string.ascii_letters + '_+-')
    _MULTIPLE_CHOICE_AUTO = { '+': CORRECT, '-': INCORRECT,
                              '_': NOT_MARKED, '': NOT_MARKED,
                              None: NOT_MARKED }

    def char_idx(self, char):
        '''
        Convert 'char' string to its index position in the alphabet.
        '''

        char = char.lower()
        if char in LETTERS:
            return ord(char) - self._ORD_A
        else:
            raise ValueError('string is not a valid letter: %s' % char)

    def iresponse_char_feed(self):
        return self._CHAR_FEED

    def iresponse_convert(self, ans):
        '''
        Convert interactive answer into its JSON form. This function supports
        many 'ans' inputs. See the examples bellow.
        
        Examples
        --------
        
        Consider the following structure
        
        >>> node = { 'type': 'multiple-choice',
        ...          'stem': 'Mark the answer to the ultimate question',
        ...          'items': [
        ...              { 'value': 0, 'text': '12', 'id': 1 },
        ...              { 'value': 1, 'text': '42', 'id': 0 },
        ...              { 'value': 0, 'text': '10', 'id': 2 },
        ...          ],
        ...        }
        >>> node = MultipleChoice(node)

        The argument 'ans' can be a single letter character        
        >>> node.iresponse_convert('c')
        2
        
        The answer can be an invalid letter.
        >>> node.iresponse_convert('d')
        {u'answer': u'd', u'type': u'invalid'}
        
        The symbols '+' and '-' designate right and wrong choices.
        >>> node.iresponse_convert('+')
        {u'answer': u'+', u'type': u'manual', u'value_pc': 100.0}
        >>> node.iresponse_convert('-')
        {u'answer': u'-', u'type': u'manual', u'value_pc': 0.0}
        
        The user can also specify a numeric percentage value to the answer
        >>> node.iresponse_convert('33.5')
        {u'answer': u'33.5', u'type': u'manual', u'value_pc': 33.5}
        
        Finally, it can pick up the best of two questions
        >>> node.iresponse_convert('a or b') # '0 'is the id for correct response 'b'
        0
        
        '''
        node = self._json
        ans_lower = ans.lower()

        # Check if ans is a single letter
        if ans_lower in LETTERS:
            idx = self.char_idx(ans_lower)
            if idx >= len(node['items']):
                return INVALID(ans).to_dict()
            else:
                return node['items'][idx]['id']

        # Try any of the automatic conversions
        try:
            return self._MULTIPLE_CHOICE_AUTO[ans](ans).to_dict()
        except KeyError:
            pass

        # Check if it is a percentage
        try:
            number = float(ans)
        except ValueError:
            pass
        else:
            return VALID(ans, number).to_dict()

        # Check if it is an 'or'
        if ' or ' in ans_lower:
            options = ans_lower.split(' or ')
            get_value = self.iresponse_convert
            values = [ get_value(o) for o in options ]

            # Check if the right answer is in values
            right_items = self.subitems_right()
            for right in right_items:
                if right['id'] in values:
                    return right['id']
            else:
                pass
                return values

    def iresponse_right(self, short=True):
        #TODO: only works with single answers
        idx = self.id_index(self.subitems_right()[0]['id'])
        return string.ascii_lowercase[idx]

    def iresponse_valid_syntax(self, ans):
        # Answer can be a letter
        if ans in string.ascii_letters:
            return True

        # ... or a number
        try:
            float(ans); return True
        except ValueError:
            pass

        #TODO: or an or
        return False

    def iresponse_complete(self, ans):
        return True

    def iresponse_marked(self, short=True):
        if 'response' not in self:
            return '_'
        else:
            response = self['response']
            try:
                idx = self.id_index(response)
                return string.ascii_lowercase[idx]
            except ValueError:
                return response['answer']

class TrueFalse(Node, HasGrades, HasItems):
    SCHEMA = schemas.TrueFalse

    # Grading ------------------------------------------------------------------
    def iresponse_right(self, short=True):
        if short:
            ans_str = { True: 'T', False: 'F' }
        else:
            ans_str = { True: 'True', False: 'False' }
        return ''.join([ ans_str[item['answer']] for item in self.subitems() ])

    _CHAR_FEED = set('TFVtfv_')
    def iresponse_char_feed(self):
        return self._CHAR_FEED

    _VALID_ANSWERS = set('true false t f verdadeiro falso v f empty'.split())
    def iresponse_valid_syntax(self, ans):
        return ans.lower() in self._VALID_ANSWERS


class Association(Node, HasGrades, HasItems):
    SCHEMA = schemas.Association
    ROMANS = ('I II III IV V VI VII VIII IX X XI XII XIII XIV XV XVI XVII '
              'XVIII XIX XX XXI XXII XXIII XXIV XXV').split()

    def grade(self, silent=True):
        resp = self.get('response', None)
        if resp is None:
            return 0.0

        img = self.get('image_ordering', range(len(self['items'])))
        img = [ i for i in img if self['items'][i]['text_domain'] ]
        return self.get('value', 1.0) * sum(i == j for i, j in zip(resp, img)) / self.num_domain_items()

    def iresponse_right(self, short=True):
        obj = self._json
        image = obj.get('image_ordering', range(len(obj['items'])))
        answers = [ string.ascii_lowercase[i] for i in image if self['items'][i]['text_domain'] ]
        return ''.join(answers)

    def iresponse_marked(self, short=True):
        if 'response' in self:
            return '<%s>' % (''.join(('_' if i is None else string.ascii_lowercase[i]) for i in self['response']))
        else:
            return '<%s>' % ('_' * self.num_domain_items())

    def iresponse_convert(self, ans):
        ans = ans[1:-1]
        def idx(c):
            try:
                return string.ascii_lowercase.index(c)
            except ValueError:
                return None

        ans_idx = [ idx(c) for c in ans.lower() ]
        return ans_idx

    def iresponse_char_feed(self):
        return set()

    def iresponse_read(self, buffer):
        N = self.num_domain_items() + 2
        return buffer[:N], buffer[N:]

    def num_domain_items(self):
        return sum(1 for item in self['items'] if item.get('text_domain', None))

    def iresponse_complete(self, ans):
        if len(ans) == self.num_domain_items() + 2:
            if ans.startswith('<') and ans.endswith('>'):
                return True
        return False

class Text(Node):
    SCHEMA = schemas.Text

#===============================================================================
#                                Learning object
#===============================================================================
class LearningObj(HasGrades, HasContent):
    SCHEMA = schemas.LearningObj
    CONTENT_TYPES = { 'multiple-choice': MultipleChoice,
                      'true-false': TrueFalse,
                      'association': Association,
                      'text': Text, }

    def value(self):
        # The grade is null if all sub-nodes were nullified
        if self.value_denorm() == 0.0:
            return 0.0
        else:
            return self.get('value', 1.0)

    # Grading ------------------------------------------------------------------
    def grade(self, silent=True):
        value = self.value()
        normalization = self.value_denorm()

        # Normalize result
        graded_subs = sum(sub.grade(silent) for sub in self.content_objects() if isinstance(sub, HasGrades))
        if value and graded_subs:
            return value * graded_subs / normalization
        else:
            return 0.0

    def value_denorm(self):
        return sum(sub.value() for sub in self.content_objects() if isinstance(sub, HasGrades))

    def iresponse_right(self, short=True):
        joint = ('' if short else ';')
        nodes = (node for node in self.content_objects() if isinstance(node, HasGrades))
        nodes = (node.iresponse_right(short) for node in nodes)
        return joint.join(nodes)

#===============================================================================
#                                Learning object
#===============================================================================
class Exam(HasGrades, HasContent):
    SCHEMA = schemas.Exam
    CONTENT_TYPES = { None: LearningObj }

    # Direct access to flat nodes ----------------------------------------------
    def flat_nodes_names(self, filter_grades=True):
        for (name, _) in self.flat_nodes_info():
            yield name

    def flat_nodes_info(self, filter_grades=True):
        lobj_no = -1
        for lobj in self.content_objects():
            item_no = -1
            lobj_no += 1

            for node in lobj.content_objects():
                if isinstance(node, HasGrades):
                    item_no += 1
                    yield (NodeIdx(lobj_no, item_no), node)
                else:
                    if not filter_grades:
                        yield (NodeIdx(lobj_no, None), node)

    # Grading ------------------------------------------------------------------
    grade = LearningObj.grade.im_func
    value_denorm = LearningObj.value_denorm.im_func

    def iresponse_right(self, short=True):
        nodes = (node.iresponse_right(short) for node in self.content_objects())
        return ';'.join(nodes)

    def iresponse_marked(self):
        marked = []
        for _, node in self.flat_nodes_info():
            marked.append(node.iresponse_marked())
        return ''.join(marked)

#===============================================================================
#                                Grading class
#===============================================================================
class NodeIdx(object):
    def __init__(self, lobj, node):
        self.lobj = lobj
        self.node = node

    def __str__(self):
        lobj, node = self.lobj, self.node
        if node is None:
            return ''
        else:
            return '%s.%s)' % (lobj + 1, string.ascii_lowercase[node])

    def get_node(self, exam):
        lobj = exam['content'][self.lobj]
        node_no = -1
        for node in lobj['content']:
            if node['type'] != 'text':
                node_no += 1
                if node_no == self.node:
                    return node

    def as_tuple(self):
        return (self.lobj, self.node)

    def __eq__(self, other):
        return (self.lobj == other.lobj) and (self.node == other.node)



class MissingAnswer(ValueError):
    def __init__(self, answer, *args):
        super(MissingAnswer, self).__init__(*args)
        self.answer = answer

    def __str__(self):
        return 'missing answer: %s' % self.answer

class IncompleteAnswer(ValueError):
    def __init__(self, answer, *args):
        super(IncompleteAnswer, self).__init__(*args)
        self.answer = answer

    def __str__(self):
        return ("incomplete answers in %s" % self.answer)

class TooManyAnswers(ValueError):
    def __init__(self, answer, *args):
        super(TooManyAnswers, self).__init__(*args)
        self.answer = answer

    def __str__(self):
        return 'too many answers: %s' % self.answer

class InvalidAnswer(ValueError):
    def __init__(self, answer, ans_value, *args):
        super(InvalidAnswer, self).__init__(*args)
        self.answer = answer
        self.ans_value = ans_value

    def __str__(self):
        return 'invalid answer: %s' % self.answer

class Grader(object):
    def __init__(self):
        self._void_nodes = set()
        self._cancel_nodes = set()

    def void_item(self, lobj, node=None):
        if node is None:
            self._void_nodes.add(lobj)
        else:
            self._void_nodes.add((lobj, node))

    def cancel_item(self, lobj, node=None):
        if node is None:
            self._cancel_nodes.add(lobj)
        else:
            self._cancel_nodes.add((lobj, node))

    def grade(self, exam, answers, update=True, silent=False):
        if not update:
            # TODO: copy object
            raise

        buffer = answers
        exam_obj = Exam(exam)
        for node_idx, node in exam_obj.flat_nodes_info():
            # Tries to feed answers to all nodes. If some node fails to get a valid
            # answer or something unexpected happens, it raises a suitable error.
            try:
                ans, buffer = node.iresponse_read(buffer)
            except ValueError:
                raise MissingAnswer(node_idx)
            if not node.iresponse_complete(ans):
                raise IncompleteAnswer(node_idx)

            # Get response
            node_tuple = node_idx.as_tuple()
            if (node_tuple in self._cancel_nodes) or (node_idx.lobj in self._cancel_nodes):
                response = { u'type': u'manual', u'value_pc': 100.0, u'answer': ans }
            elif (node_tuple in self._void_nodes) or (node_idx.lobj in self._void_nodes):
                response = { u'type': u'manual', u'value_pc': 0.0, u'answer': ans }
                node['value'] = 0.0
            else:
                response = node.iresponse_convert(ans)
                if (not silent) and isinstance(response, dict) and response['type'] == 'invalid':
                    raise InvalidAnswer(node_idx, ans)

            # Save response
            if response is None:
                if 'response' in node:
                    del node[u'response']
            else:
                node[u'response'] = response

        # Check if buffer is empty
        if not buffer:
            return exam_obj.grade(silent)
        else:
            raise TooManyAnswers(buffer)

    def grade_interactive(self, exam, answers='', update=True, silent=False, print_invalid=1, print_final=True):
        print("Grading Exam: '%s'" % exam['name'])
        grade_exam = self.grade

        while True:
            try:
                grade = grade_exam(exam, answers, update, silent)
                break
            except (MissingAnswer, IncompleteAnswer) as ex:
                answers += raw_input('  ' + str(ex.answer).ljust(5))
            except TooManyAnswers:
                marked = Exam(exam).iresponse_marked()
                ans = raw_input('Too many answers. Truncate to %s? (y/n) ' % marked)
                if 'y' in ans:
                    answers = marked
                else:
                    answers = ''
            except InvalidAnswer as ex:
                print '  %s invalid answer: %s' % (ex.answer, ex.ans_value)
                answers = []
                for node_idx, node in Exam(exam).flat_nodes_info():
                    if node_idx == ex.answer:
                        break
                    answers.append(node.iresponse_marked(short=False))
                answers = ';'.join(answers)

        # Print invalid nodes
        if print_invalid:
            bad_responses = []
            for node_idx, node in Exam(exam).flat_nodes_info():
                if node.grade() < node.value():
                    right = node.iresponse_right()
                    marked = node.iresponse_marked()
                    value = 100.0 * node.grade() / node.value()
                    if print_invalid >= 2:
                        bad_responses.append('  %s *%s*, marked %s (%s%%)' % (node_idx, right, marked, value))
                    else:
                        bad_responses.append(str(node_idx))
            if bad_responses:
                if print_invalid >= 2:
                    print '\nBad responses:'
                    print '\n'.join(bad_responses)
                else:
                    print '\nBad responses: %s' % (', '.join(bad_responses))

        if print_final:
            # Print final grade
            print '\nGrade: %.2f/%.2f' % (grade, exam.get('value', 1))
        return grade

#===============================================================================
#                 Funções para consertar erros no objeto JSON
#===============================================================================
def to_value(obj):
    try:
        obj[u'value'] = obj['grade']
        del obj['grade']
    except KeyError:
        pass
    items = obj.get('content', obj.get('items', []))
    for item in items:
        to_value(item)
    return obj

def lista5_fix(obj):
    # Esqueceu de setar 'value' em questões
    item = MultipleChoice(obj['content'][7]['content'][2])
    idx = item.id_index(0)
    item['items'][idx][u'value'] = 1.0

    item = MultipleChoice(obj['content'][10]['content'][2])
    idx = item.id_index(0)
    item['items'][idx][u'value'] = 1.0

def lista3_fix(obj):
    # Criar questáo fake para 
    Q = {'content': [ {'type': 'multiple-choice', 'items': [ {'id': i} for i in range(9)]} ]}
    if len(obj['content']) == 9:
        obj['content'].insert(5, Q)
    obj = to_value(obj)
    obj['value'] = 6.0
    return obj

#===============================================================================
#             Funções para corrigir listas/provas específicas
#===============================================================================
def corrigir_lista3():
    import simplejson

    with open('../visualization/json_consolidated') as F:
        objects = simplejson.load(F)['unique']

    # Setup grader
    grader = Grader()
    grader.void_item(0)
    grader.void_item(5)
    grader.void_item(7)
    grader.void_item(1, 0)
    grader.void_item(6, 0)

    folder = '../visualization/dumps-lista3/'
    key_base = u'cálculo 3/módulo 3/lista::%s'

    while True:
        try:
            idx = unicode(raw_input('\n# da lista: '))
            key = key_base % idx
            obj = objects[key]
        except KeyError:
            print u'Prova inválida: %s' % key
            continue

        lista3_fix(obj)
        nota_lista = grader.grade_interactive(obj)
        print 'Nota da lista: %.2f' % (max(0, nota_lista - 3))

        file = '%s.json' % idx
        if os.path.exists(file):
            file += '2'
        with open(os.path.join(folder, file), 'w') as F:
            simplejson.dump(obj, F)

def corrigir_prova4(cancel4=False):
    import simplejson

    basepath = '../visualization/dumps-prova/%s.json'
    graded = '../visualization/dumps-prova/graded-%s.json'
    gp = Grader()
    if cancel4:
        gp.void_item(3)

    while True:
        try:
            idx = unicode(raw_input('\n# da prova: '))
            with open(basepath % idx, 'r') as F:
                obj = simplejson.load(F)
                obj['value'] = 10.0
        except IOError:
            print u'Prova inválida: %s' % (basepath % idx)
            continue

        nota_lista = gp.grade_interactive(obj, print_invalid=2)
        #if not LearningObj(obj['content'][3]).grade():
        #    nota_lista *= 5. / 4.
        print 'Nota da prova: **%.2f**' % nota_lista

        file = graded % idx
        if os.path.exists(file):
            file += '2'
        with open(os.path.join(file), 'w') as F:
            simplejson.dump(obj, F)

def corrigir_lista4():
    import simplejson
    basepath = '../visualization/lista4-dumps/lista-%s.json'
    graded = '../visualization/lista4-dumps/graded-%s.json'
    gp = Grader()
    gp.cancel_item(3)
    gp.cancel_item(4)

    while True:
        try:
            idx = unicode(raw_input('\n# da prova: '))
            with open(basepath % idx, 'r') as F:
                obj = simplejson.load(F)
                obj['value'] = 6.0
        except IOError:
            print u'Prova inválida: %s' % (basepath % idx)
            continue

        nota_lista = gp.grade_interactive(obj, print_invalid=2)
        print 'Nota da lista: **%.2f**' % max(nota_lista - 3.0, 0.0)

        file = graded % idx
        if os.path.exists(file):
            file += '2'
        with open(os.path.join(file), 'w') as F:
            simplejson.dump(obj, F)


#===============================================================================
#                                     Doctests
#===============================================================================
if __name__ == '__main__':
    import doctest
    doctest.testmod(optionflags=doctest.REPORT_ONLY_FIRST_FAILURE)

if __name__ == '__main__':
    pass
#    from tutor.data.tutor_lib import get_exam
#    from tutor.transforms import creation
#    from tutor import visualization
#    import simplejson
#    with open('../visualization/lista4-dumps/lista-1.json') as F:
#        obj = simplejson.load(F)
#        obj['value'] = 10
#
#    grader = Grader()
#    print grader.grade(obj, 'bcachahad<abdc><adbc><bdfacghe><ab><acbd>')
#    print grader.grade_interactive(obj, 'bcachahad<abdc><adbc><bdfacghe><ab><acbd>', print_invalid=2)
#    print grader.grade_interactive(obj, 'hbib100', print_invalid=2)
