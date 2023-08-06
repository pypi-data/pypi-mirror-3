from __future__ import print_function
from future_builtins import *
import random
from tutor.config import schemas
from tutor.util import jsonlib7
from tutor.db.base import Printable

#===============================================================================
#                          NODES --- Base types
#===============================================================================
class Node(Printable):
    types = {}
    def __new__(cls, json=None, parent=None, **kwds):
        """
        Node objects are containers that represent an specific type of question
        such as multiple choice, true/false, etc.
        
        Input
        -----
            json : dict
                Data content for Node object
                
            kwds : dict
                Extra fields to update json dict
                
            parent (optional):
                Parent node/LearningObj
        """

        # Inspect type on creation of Node objects
        if cls is Node:
            try:
                tt = json['type']
            except KeyError:
                raise TypeError('unspecified Node type')

            return Node.types[tt](json, parent, **kwds)

        else:
            return  object.__new__(cls)

    def __init__(self, json=None, parent=None, **kwds):
        json = json if json is not None else {}
        json.update(kwds)
        self._json = (json if json is not None else {})
        self.parent = parent

    @property
    def has_parent(self):
        return self.parent is None

    @property
    def location(self):
        if self.parent is None:
            return None
        else:
            idx = self.parent.content.index(self)
            return '%s.%s' % (self.parent.name, idx)

    def refresh(self):
        '''
        This method is called whenever the node is created by copying from a
        template. The default action is to randomize content when it is allowed
        by the Node object.
        '''
        return

    def __nonzero__(self):
        return bool(self._json)

    def __eq__(self, other):
        try:
            return self._json == other._json
        except AttributeError:
            return None

class HasAnswers(Node):
    pass

class HasItems(HasAnswers):
    item_key = 'items'

    def add_item(self, item):
        """
        Adds an Item object 'item' to the current question. 
        
        If 'check' is True (default), it prevents identical choices to be 
        inserted.
        """

        # retrieve json
        if isinstance(item, dict):
            json = item
        else:
            json = item.json

        # append item
        try:
            self._json[self.item_key].append(json)
        except KeyError:
            self._json[self.item_key] = [ json ]

        # set parent if not set
        if (item.parent is None) or (item.parent is self):
            item.parent = self
        else:
            raise ValueError('item must have a single parent')

    def assert_unique_items(self, key='text'):
        '''
        Check if all items have unique values for a given 'key'.
        '''

        values = jsonlib.jpath(self._json, '$.{0}.*.{1}'.format(self.item_key, key))
        values_set = set(values)
        
        if  len(values) != len(values_set):
            rep_values = list(values)
            for v in values_set:
                idx = rep_values.index(v)
                del rep_values[idx]
            rep = rep_values.pop()

            idx1 = [ x[key] for x in self._json['items']].index(rep)
            idx2 = [ x[key] for x in self._json['items']].index(rep, idx1 + 1)
            path = self.parent.name + '.items'
            
            raise ValueError("repeated value in '$.%s[%s,%s]': %s" % (path, idx1, idx2, rep))

    @property
    def item_list(self):
        return self.json[self.item_key]

    def refresh(self):
        if self.shuffle:
            random.shuffle(self._json['items'])

#===============================================================================
#                       NODES --- Consumer node types
#===============================================================================
@jsonlib.json_properties(schemas.Text)
class Text(Node):
    """
    Intro objects hold plain text json introducing a question or a series of 
    questions. Do not confuse with the stem of a question. The json is 
    in the form of LaTeX source.
    """
    def latex(self, **kwds):
        return self.text
Node.types['text'] = Text

@jsonlib.json_properties(schemas.MultipleChoice)
class MultipleChoice(HasItems):
    """
    MultipleChoice objects implements multiple-choice questions
    """

    def T_items_in(self, obj):
        return [ item.json_raw for item in obj ]

    def T_items_out(self, obj):
        if obj is None:
            return []
        else:
            return [ MultipleChoiceItem(item, self) for item in obj ]

    def latex_tabular_header(self):
        size = (0.9 - self.columns / 45.) / self.columns
        col_header = '>{\\raggedright}p{%.3f\\textwidth}' % size
        return '{%s}' % (col_header * self.columns)

    def latex_rows(self):
        letters = list('abcdefghijklmnopqrstuvwxyz')
        elems = list(self.items)
        rows = []

        # Create each row
        N, Nc = len(self.items), max(self.columns, 1)
        N_rows = N / Nc + int(bool(N % Nc))

        for n in range(N_rows):
            cols = []
            for m in range(Nc):
                try:
                    elem = elems.pop(0).latex()
                    letter = '%s) ' % letters.pop(0)
                except IndexError:
                    elem = ''
                    letter = ''
                cols.append(letter + elem)
            rows.append(' & '.join(cols))

        return rows

    def refresh(self):
        super(MultipleChoice, self).refresh()
        for item in self.items:
            item.grade = float(item.grade)

#    def compute_grade(self, ans, full_output=False):
#        try:
#            grade = self.fixed_grade
#        except:
#            if not ans is None:
#                grade = self.items[ans].grade
#            else:
#                grade = None
#
#        # format output
#        if full_output:
#            right_ans = self.answer
#            right_grade = self.items[right_ans].grade
#            return (ans, grade, right_ans, right_grade)
#        else:
#            return grade
#
#    @property
#    def answer(self):
#        ans_idx = None
#        grade = 0
#        for idx, item_grade in enumerate(item.grade for item in self.items):
#            if item_grade > grade:
#                grade = item_grade
#                ans_idx = idx
#        return ans_idx
#
#    def read_answers(self, answers, code):
#        # read from input if answers is empty
#        if not answers:
#            answers = raw_input('Answer (q %s): ' % code)
#        try:
#            ans, answers = answers[0], answers[1:]
#        except IndexError:
#            ans = ' '
#            answers = ''
#
#        # process answer
#        if ans == ' ':
#            grade = getattr(self, 'fixed_grade', 0)
#            return (grade, None), answers
#        elif ans == '*':
#            grade = getattr(self, 'fixed_grade', max(self.grades))
#            return (grade, None), answers
#        else:
#            ans_n = ord(ans.lower()) - ord('a')
#            if ans_n >= len(self.items):
#                raise ValueError("Invalid answer '%s' for '%s'" % (ans, code))
#
#        # extract the grade
#        try:
#            grade = self.fixed_grade
#        except:
#            grade = self.items[ans_n].grade
#
#        return (grade, ans_n), answers
#
#    def fmt_answer(self, ans):
#        if ans is None:
#            return None
#        else:
#            return chr(ans + ord('a'))
#
#    def nullify(self, assign_grade=True):
#        if not assign_grade:
#            grade = 0
#        else:
#            grade = max(self.grades)
#
#        self.json['fixed_grade'] = grade
#        self.parent.save()
#
#    @property
#    def grades(self):
#        return [ item.grade for item in self.items ]
Node.types['multiple-choice'] = MultipleChoice

@jsonlib.json_properties(schemas.TrueFalse)
class TrueFalse(HasItems):
    """
    TrueFalse objects implements True/False questions
    """
    def T_items_in(self, obj):
        return [ item.json_raw for item in obj ]

    def T_items_out(self, obj):
        if obj is None:
            return []
        else:
            return [ TrueFalseItem(item, self) for item in obj ]

#    @property
#    def answer(self):
#        return True
#
#    def compute_grade(self, ans, full_output=False):
#        right_ans = self.answer
#        grade = sum(map(lambda x, y: (x if x is None else int(x == y)), ans, right_ans))
#
#        if full_output:
#            return (ans, grade, right_ans, len(self.items))
#        else:
#            return grade
#
#    def read_answers(self, answers, code):
#        # read from input if answers is empty
#        return (0, 1), answers
#
#        if not answers:
#            answers = raw_input('Answer (q %s): ' % code)
#        try:
#            ans, answers = answers[0], answers[1:]
#        except IndexError:
#            ans = ' '
#            answers = ''
#
#        # process answer
#        if ans == ' ':
#            grade = getattr(self, 'fixed_grade', 0)
#            return (grade, None), answers
#        else:
#            ans_n = ord(ans.lower()) - ord('a')
#            if ans_n >= len(self.items):
#                raise ValueError("Invalid answer '%s' for '%s'" % (ans, code))
#
#        # extract the grade
#        try:
#            grade = self.fixed_grade
#        except:
#            grade = self.items[ans_n].grade
#
#        return (grade, ans_n), answers
#
#    def fmt_answer(self, ans):
#        if ans is None:
#            return None
#        else:
#            return chr(ans + ord('a'))
#
#    def nullify(self, assign_grade=True):
#        if not assign_grade:
#            grade = 0
#        else:
#            grade = max(self.grades)
#
#        self.json['fixed_grade'] = grade
#        self.parent.save()
#
#    @property
#    def grades(self):
#        return [ item.grade for item in self.items ]
Node.types['true-false'] = TrueFalse

@jsonlib.json_properties(schemas.TrueFalseItem)
class TrueFalseItem(Node):
    def pretty(self):
        return '(%s) %s' % (self.answer, self.text.strip())

    def latex(self, **kwds):
        return '\\begin{tabular}{|c|c|}\\hline V & F \\\\ '\
               '\\hline\\end{tabular} ' + self.text

@jsonlib.json_properties(schemas.Association)
class Association(HasItems):
    """
    Association objects implements association questions
    """
    def T_items_in(self, obj):
        return [ item.json_raw for item in obj ]

    def T_items_out(self, obj):
        if obj is None:
            return []
        else:
            return [ AssociationItem(item, self) for item in obj ]
Node.types['association'] = Association

@jsonlib.json_properties(schemas.AssociationItem)
class AssociationItem(Node):
    def pretty(self):
        return '(%s) %s' % (self.answer, self.text.strip())

    def latex(self, **kwds):
        return '[{\\begin{tabular}{|c|c|}\\hline V & F \\\\ '\
               '\\hline\\end{tabular}}] ' + self.text

@jsonlib.json_properties(schemas.MultipleChoiceItem)
class MultipleChoiceItem(Node):
    def pretty(self):
        return '(%s) %s' % (self.grade, self.text.strip())

    def latex(self, **kwds):
        return self.text

#__all__ = [ 'Node', 'MultipleChoice', 'TrueFalse', 'Text', 'Item' ] + \
#            'STATUS_OK, STATUS_PENDING, STATUS_TESTED, STATUS_INVALID, ' \
#            'STATUS_VOID'.split(', ')

if __name__ == '__main__':
#    # TrueFalse
#    n = TrueFalse(shuffle=True, stem='Answer this')
#    n.add_item(TrueFalseItem(answer=False, text='Bla'))
#    n.add_item(TrueFalseItem(answer=True, text='Blu'))
#    print(n.pretty())
#    print(n.latex())
#
#    # multiple choice
#    n = MultipleChoice(stem='Blah blah blah?')
#    n.add_item(MultipleChoiceItem(grade=1.0, text='Foo', feedback='Bar'))
#    n.add_item(MultipleChoiceItem(grade=0.5, text='Bar', feedback='Foo'))
#    n.add_item(MultipleChoiceItem(grade=0, text='FooBar', feedback='BarFoo'))
#    n.pprint()
#    print(n.latex())
    MC = dict(stem='Foo',
              columns=2,
              items=[dict(text='foo', grade=1),
                     dict(text='bar', grade=1),
                     dict(text='eggs', grade=1)])
    mc = MultipleChoice(MC)
    print(mc.latex())
