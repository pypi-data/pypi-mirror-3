from __future__ import absolute_import, print_function, unicode_literals, division
from future_builtins import * #@UnusedWildImport
if __name__ == '__main__':
    __package__ = b'tutor.types' #@ReservedAssignment
    import tutor.types #@UnusedImport

import random
from decimal import Decimal
from ..util.relational import ManyToOne
from .response import NoResponse, Response
from .schema import (SchemaObj, sch_instance, Opt, array_of,
                                Array, Str, Dict, Bool,
                                Number, Null, Type, Object)

class FormatingError(ValueError):
    pass

class SubQuestion(SchemaObj):
    schema = Object({'text': Str()})
    parent = ManyToOne()

    def question_index(self):
        '''Determines the sub-question position amongst its siblings.'''

        return self.parent.body.index(self)

    @property
    def ref(self):
        return self.parent.ref + (self.question_index(),)

    def copy(self, keep_parent=True):
        new = super(SubQuestion, self).copy()
        if keep_parent:
            new.parent = self.parent
        return new

    def format(self, renderer): #@ReservedAssignment
        '''Apply function 'renderer' to strings attributes in object'''

        for key, sch in self.schema.items():
            value = getattr(self, key)
            if isinstance(sch, Str) or isinstance(sch, Opt) and isinstance(sch.schema, Str):
                value = renderer(value)
                setattr(self, key, value)
            elif (isinstance(sch, Array) and  isinstance(sch.array_t, Type) and issubclass(sch.array_t.type, SubQuestion)):
                for item in value:
                    item.format(renderer)

    def feedback(self, response):
        return None

    def response(self, data, **kwds):
        '''Returns a response object from given data'''

        return Response(self, data=data, **kwds)

    def score(self, response):
        raise NotImplementedError('must be implemented in subclasses')

class Pseudo(object):
    '''
    Emulates other SchemaObj objects. Useful to assign data to an object's 
    parent when the parent does not exist.  
    '''
    def __init__(self, **kwds):
        for k, v in kwds:
            setattr(self, k, v)

    @property
    def dictview(self):
        return self.__dict__


    # Methods ------------------------------------------------------------------
    def score(self, markings):
        '''Compute a normalized score (between 0 and 1) corresponding to the
        given markings'''
        raise

#===============================================================================
# Subquestions
#===============================================================================
class IntroText(SubQuestion):
    json_name = 'tutor.question.introtext'
    class schema(sch_instance):
        text = Str()

    def score(self, response):
        if not isinstance(response, NoResponse):
            raise TypeError('only accept empty responses')
        return Decimal(0)

    def response(self, data, **kwds):
        if data is not None:
            raise ValueError('cannot assign non-null data to empty responses')
        return NoResponse(self, **kwds)

    @property
    def value(self):
        return Decimal(0)

class Scoring(SubQuestion):
    schema = Object({'value': Number(Decimal(0))})

    def question_index(self, scoring=False):
        '''Determines the sub-question position amongst its siblings. If 
        scoring is True (default is False) consider only scoring elements'''

        if scoring:
            body = (x for x in self.parent.body if isinstance(x, Scoring))
            for i, x in enumerate(body):
                if x is self:
                    return i
            else:
                raise ValueError('%s not in list' % self)
        else:
            return super(Scoring, self).question_index()

class MultipleChoiceItem(SubQuestion):
    json_name = 'tutor.question.multiplechoiceitem'
    class schema(sch_instance):
        text = Str('')
        value = Number(Decimal(0))
        feedback = Str('')

    def __init__(self, **kwds):
        super(MultipleChoiceItem, self).__init__(**kwds)
        self.value = Decimal(self.value)

    def iscorrect(self):
        return self.value == self.parent.maxvalue

class MultipleChoice(Scoring):
    json_name = 'tutor.question.multiplechoice'
    class schema(sch_instance):
        stem = Str('')
        multiple_answers = Bool(False)
        value = Number(Decimal(1))
        shuffle = Bool(True)
        order = Array()
        columns = Number(0)
        post_process = Dict({})
        items = Array(Type(MultipleChoiceItem))

    def __init__(self, **kwds):
        kwds.setdefault('items', [])
        super(MultipleChoice, self).__init__(**kwds)
        self.value = Decimal(self.value)
        for item in self.items:
            item.parent = self

    def adapt(self, inplace=False, **kwds):
        if inplace:
            super(MultipleChoice, self).adapt(inplace=True, **kwds)
            self.value = Decimal(self.value)
            return self
        else:
            return super(MultipleChoice, self).adapt(inplace=True, **kwds)

    def format(self, renderer):
        super(MultipleChoice, self).format(renderer)
        if self.shuffle:
            order = list(range(len(self.items)))
            random.shuffle(order)
            self.order = order

        for item in self.items:
            if item.text == '$$':
                item.text = '$ $'

        texts = [ item.text for item in self.items ]
        if len(texts) != len(set(texts)):
            for text in set(texts):
                texts.remove(text)
            raise FormatingError('repeated sub-items: "%s"' % texts[0])

    def score(self, response):
        '''Computes the sub-question score from the given markings.
        
        Parameters
        ----------
        response : sequence
            A response object. The data attribute of the response object must
            be  a sequence of items marked by the student. A empty sequence means 
            that the question was left blank. A sequence with more than one 
            item means that several alternatives were marked.
        '''

        rdata = response.data

        if not rdata:
            return Decimal(0)
        if self.multiple_answers:
            raise NotImplementedError
        else:
            if len(rdata) == 1:
                norm = self.maxvalue
                marked = next(iter(rdata))
                return self.items[marked].value / norm * Decimal(self.value)
            else:
                return Decimal(0)

    def additem(self, text, value=0, **kwds):
        '''Adds a new multiple choice item'''

        item = MultipleChoiceItem(text=text, value=value, **kwds)
        self.items.append(item)
        item.parent = self

    def validate(self, **kwds):
        '''Validates object.'''

        super(MultipleChoice, self).validate(**kwds)

        if self.maxvalue == 0:
            raise ValueError('maxvalue cannot be zero')

        order = self.order
        if len(order) != len(self.items):
            raise ValueError('order should have %s items, got %s' %
                             (len(self.items), len(order)))
        if set(range(len(order))) != set(order):
            raise ValueError('repeated numbers in order, got: %s' % order)

    # Properties ---------------------------------------------------------------
    @property
    def order(self):
        try:
            return self._data['order']
        except KeyError:
            return range(len(self.items))

    @order.setter
    def order(self, value): #@DuplicatedSignature
        self._data['order'] = value

    @property
    def maxvalue(self):
        '''Greatest value of all items in the multiple choice question.'''

        maxvalue = max(x.value for x in self.items)
        if maxvalue == 0:
            raise ValueError('maximum value is null')
        return Decimal(maxvalue)

    @property
    def correct_idx(self):
        '''Return a list of indexes of the right answer(s)'''

        maxvalue = self.maxvalue
        return [ i for (i, item) in enumerate(self.items) if item.value == maxvalue ]

    def copy(self, keep_parent=True):
        new = super(MultipleChoice, self).copy(keep_parent)
        new_items = []
        for item in self.items:
            new_item = item.copy()
            new_item.parent = new
            new_items.append(new_item)
        return new

class TrueFalse(SubQuestion):
    class schema(sch_instance):
        stem = Str('')
        value = Number(1)
        answer = Bool()
        text = Str()
        text_other = Str('')

class TrueFalseGroup(SubQuestion):
    class schema(sch_instance):
        stem = Str('')
        value = Number(1)

        class items(array_of):
            text = Str()
            text_other = Str('')
            answer = Bool()
            value = Number(1)
            feedback = Str('')

class Association(SubQuestion):
    class schema(sch_instance):
        stem = Str('')
        value = Number(1)

        class items(array_of):
            text = Str() | Null()
            image = Str() | Null()
            value = Number(0)
            feedback = Str('')

import warnings, types

class decimalMul(object):
    if not getattr(Decimal, '_changed', False):
        oldmul = staticmethod(Decimal.__mul__.im_func)

    def __get__(self, obj, tt=None):
        if obj is None:
            return self

        def mul(this, other, context=None):
            if isinstance(other, float):
                warnings.warn('float here!')
                other = Decimal(other)
            return self.oldmul(this, other, context)

        return types.MethodType(mul, obj, tt)

Decimal.__mul__ = decimalMul()
Decimal._changed = True

if __name__ == '__main__':
    from tutor.types.question import QuestionPool

    m = MultipleChoice()
    m.additem('foo', 1)
    m.additem('bar', 0)
    print(m.order)
    print(m.dictview)
    m.validate()




