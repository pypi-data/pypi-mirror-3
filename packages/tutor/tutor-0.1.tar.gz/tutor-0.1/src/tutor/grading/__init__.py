'''
tutor.grading Package
---------------------

This package implements a few convenience functions for grading Question and
Exam objects. Grades can be assigned using a special syntax described bellow.

Grading syntax
--------------

The answers can be encoded in a string using a special notation that represents
the outcomes of many different type of multiple choice questions or the grade
manually given by a teacher.

The most straightforward example is a exam with several multiple choice 
questions. In this case, the student's answers can be encoded as a sequence of 
letters, with asterisk (*) representing missing answers. Spaces are optional.

Example: If the student marked 'a' in the first question, missed the second 
question and marked 'b' in the third one, the strings 'a*b', 'a * b' and 'a* b'
will be equivalent representations of the given answers.

There is some support for manual correction, and this can be enabled/disable 
with some level of granularity upon the caller discretion. If the answer given 
by the student must receive the maximum or minimum grade, then the +/- notation 
can be used as in e.g.: '+++' to assing the maximum grade and '---' to assign 
the minimum one.

Examples
--------

In all cases, consider an exam with 4 questions, in which the first and last 
ones have a single multiple choice field with answers up to letter (e). The 
second question has 3 multiple choice fields with 5 options each and the last 
one has a multiple choice followed by a true/false field.

Consider that the student marked 'a' in the first question, 'b', 'c', 'd' in 
each field of the second question and 'e' and 'false'  in the third one and the 
student skipped the last question. These answers can be represented in many 
different equivalent manners:

* Compact: "abcdef*#, "abcde false *", or "a bcd ef *", etc 
* Grouped: "(a)(bcd)(ef)(*)"
* Verbose: "1) a 2) bcd 3) e false 4) *"
* Verbose (multiple lines):
"""1) a
   2) bcd
   3a) e
   3b) false""" (implicitly omitting the skipped answer)
    
In all cases, the string is parsed to list of lists:
    answers = [[ANS(0)], [ANS(1), ANS(2), ANS(3)], [ANS(4), ANS(False)], [None]]
in which ANS represents a possible answer to the given question field.
'''


