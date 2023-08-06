#!/usr/bin/python
#-*-coding: utf8-*-
import sys
import argparse
import tutor.version
import actions

#===============================================================================
# Main Parser
#===============================================================================
parser = argparse.ArgumentParser(
  description='Control the Py-Tutor system.',
  prog='tutor', add_help=True, version='%%(prog)s %s' % tutor.version.VERSION)

parser.add_argument('--interactive', '-i',
  action='store_true', help='enable interactive mode')

parser.add_argument('--debug', '-d',
  action='store_true', help='print tracebacks')

subparsers = parser.add_subparsers(
  title='valid object commands',
  dest='object', help='tutor object commands')

#===============================================================================
# Question objects: tutor question ...
#===============================================================================
q_parser = subparsers.add_parser('question',
  help='manipulates question objects')
q_subparsers = q_parser.add_subparsers(title='valid question commands',
  dest='command')

# tutor question new "question name"
q_new = q_subparsers.add_parser('new', help='creates a new question')
q_new.add_argument('name', help='name for the new question')
q_new.add_argument('--force', '-f', action='store_true',
  help='overwrites previous question, if exists')
q_new.add_argument('--lyx', '-l', action='store_true',
  help='creates a new question with a .lyx main file')
q_new.add_argument('--main', '-m', help='path to the main.* file')
q_new.add_argument('--namespace', '--ns', '-n', help='path to the namespace.* file')
q_new.add_argument('--author', '-a', help="author's name")
q_new.add_argument('--title', '-t', help="question's title")

# tutor question commit "question name"
q_commit = q_subparsers.add_parser('commit',
  help='add questions to question file using template')
q_commit.add_argument('name', help='name of question file')
q_commit.add_argument('size', help='number of generated versions', type=int)

# tutor question view "question name"
q_view = q_subparsers.add_parser('view',
  help='render the question as a pdf file')
q_view.add_argument('name', help='name of question file')
q_view.add_argument('outfile',
                    help='output file (type "!type" to open the appropriate viewer)',
                    default=None)

# tutor question src "question name"
q_src = q_subparsers.add_parser('src',
  help="open content of question's src directory for editing")
q_src.add_argument('name', help='name of question file')
q_src.add_argument('--force', '-f', action='store_true',
  help='overwrites source directory, if exists')

#===============================================================================
# Exam objects: tutor exam ...
#===============================================================================
e_parser = subparsers.add_parser('exam',
  help='manipulates exam objects')
e_subparsers = e_parser.add_subparsers(title='valid exam commands',
  dest='command')

# tutor exam new "exam name"
e_new = e_subparsers.add_parser('new', help='creates a new exam')
e_new.add_argument('name', help='name for the new exam')
e_new.add_argument('--force', '-f', action='store_true',
  help='overwrites a previous exam, if exists')
e_new.add_argument('--author', '-a', help="author's name")
e_new.add_argument('--title', '-t', help="exam's title")

# tutor exam addq "exam name" "question name"
e_addq = e_subparsers.add_parser('addq', help='adds a new question')
e_addq.add_argument('name', help='name of exam file')
e_addq.add_argument('question', help='name of question file')
e_addq.add_argument('--force', '-f', action='store_true',
                    help='force insertion')

# tutor exam commit "exam name" "size"
e_commit = e_subparsers.add_parser('commit',
    help='add exams to exam file using template')
e_commit.add_argument('name', help='name of exam file')
e_commit.add_argument('size', help='number of generated versions', type=int)

# tutor exam view "exam name" "outfile"
e_view = e_subparsers.add_parser('view',
    help='render the question as a pdf file')
e_view.add_argument('name', help='name of exam file')
e_view.add_argument('outfile',
                    help='output file (type "!type" to open the appropriate viewer)',
                    default=None)

# tutor exam commit "exam name" "size"
e_set = e_subparsers.add_parser('setvalue',
    help='modify exam attribute')
e_set.add_argument('name', help='name of exam file')
e_set.add_argument('attr', help='name of attribute')
e_set.add_argument('value', help='new value for attribute')

#===============================================================================
# Stuent objects: tutor student ...
#===============================================================================
s_parser = subparsers.add_parser('student', help='manipulates students')
s_subparsers = s_parser.add_subparsers(title='valid student commands',
                                       dest='command')

# tutor student new "student name"
s_new = s_subparsers.add_parser('new', help='register a new student')
s_new.add_argument('name', help='name for the new student')

# tutor student delete "student name"|"student id"
s_delete = s_subparsers.add_parser('delete', help='delete a student from tutor system')

# tutor student edit "student name"|"student id"
s_edit = s_subparsers.add_parser('edit', help='edit student information')

def interactive_mode():
    raise SystemExit('Interactive mode not implemented yet...')

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    # Checks if interactive mode is enabled
    if '-i' in argv[1:] or '--interactive' in argv[1:]:
        interactive_mode()

    # Delegates action to object/command method
    else:
        args = parser.parse_args(argv)
        obj_cls = getattr(actions, args.object.title())
        obj = obj_cls()
        action = getattr(obj, args.command)
        kwargs = dict(args.__dict__)
        del kwargs['object'];  del kwargs['command']

        if args.debug:
            action(**kwargs)
        else:
            try:
                action(**kwargs)
            except Exception as ex:
                parser.error(ex)

if __name__ == '__main__':
    main()
#    main(['question', 'new', 'foo' , '-f'])
#    main(['question', 'commit', 'foo' , '10'])
