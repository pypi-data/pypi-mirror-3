from __future__ import absolute_import

from StringIO import StringIO
import pyson
from ..types import QuestionPool
from . import bin_serialize
from .base import loads, BadHeaderError
from . import base

def BadHeaderLoad(data, ex):
    if data.startswith(b'\xffTUTOR-'):
        header, _, __ = data[1:].partition('\xff')
        if header == 'TUTOR-QUESTION':
            data = bin_serialize.load(StringIO(data), '\xff%s\xff' % header, '0.1')
            return BadJSON(data, ex)
        elif header == 'TUTOR-EXAM':
            data = bin_serialize.load(StringIO(data), '\xff%s\xff' % header, '0.1')
            return BadJSON(data, ex)

    raise ex

def BadFile(data):
    raise ValueError

def BadJSON(data, ex):
    tt_mapping = {
        'datetime.datetime': 'datetime',
        'tutor.TextIntro': 'tutor.question.introtext',
        'tutor.exam.Exam': 'tutor.ExamPool',
        'tutor.IntroText': 'tutor.question.introtext',
        'tutor.MultipleChoice': 'tutor.question.multiplechoice',
        'tutor.question.src_folder.SrcFolder': 'tutor.SrcFolder',
        'tutor.question.types.TextIntro': 'tutor.question.introtext',
        'tutor.question.types.MultipleChoice': 'tutor.question.multiplechoice',
        'tutor.question.types.Question': 'tutor.QuestionPool',
        'tutor.history.History': 'tutor.History',
        'tutor.Question': 'tutor.QuestionPool'
    }
    data = [data]
    lists = {}
    for k, v in pyson.walkitems(data, ret_nodes=True):
        if isinstance(v, dict):
            if '@type' in v:
                tt = v['@type']
                if tt == 'tutor.Template':
                    pyson.setitem(data, k, v['data'])
                elif tt == 'tutor.template.types.Template':
                    pyson.setitem(data, k, v['data'])
                elif tt in tt_mapping:
                    v['@type'] = tt_mapping[tt]

                if v['@type'] == 'tutor.question.multiplechoice':
                    items = v['items']
                    for item in items:
                        item['@type'] = 'tutor.question.multiplechoiceitem'
                    if not sum(item.get('value', 0) for item in items):
                        items[0]['value'] = 1
                    if not v.get('order', True):
                        del v['order']

            if 'type' in v:
                tt = v['type']
                if tt == u'tutor-question:namespace':
                    continue
                elif tt in ['tutor-question:multiple-choice', 'tutor-question:intro', 'tutor-question', 'tutor-exam']:
                    del v['type']
                else:
                    print v.keys()
                    print v['type']
                    raise ValueError

#            if v.get('@type', None) == 'tutor.Exam':
#                if v['subtitle'] is None:
#                    del v['subtitle']

        if isinstance(v, list) and v:
            lists[k] = v

    for k, v in lists.items():
        first = v[0]
        if isinstance(first, basestring) and first.startswith('@type:'):
            v.append(v.pop(0))

        last = v[-1]
        if isinstance(last, basestring) and last.startswith('@type:'):
            tt = last[6:]
            tt = tt_mapping.get(tt, tt)
            v[-1] = '@type:' + tt
            if tt == 'tutor.Template':
                print v

    data = data[0]
    result = pyson.json_decode(data)
    result.adapt(inplace=True, force=True)
    return result
