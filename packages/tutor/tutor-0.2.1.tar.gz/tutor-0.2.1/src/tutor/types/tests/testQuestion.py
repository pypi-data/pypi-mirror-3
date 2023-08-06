#-*- coding:utf8 -*-
import nose
from tutor.types.question import *

def test_question_new():
    QuestionPool('foo')

def test_question_commit():
    qst = QuestionPool('foo')
    qst.commit(50)

if __name__ == '__main__':
    nose.main()
