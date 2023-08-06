#-*-coding: utf8-*-
from cStringIO import StringIO
import time
import optparse
from tutor.config import settings
from tutor.config import schemas


class InvalidCommandError(Exception):
    pass

class Task(object):
    def __init__(self, options, arguments, help_str):
        self.options = options
        self.arguments = arguments
        self.help_str = help_str

        # Initialize selected objects
        self.course = self.classroom = self.student = self.activity = self.task = None

        # Execute commands
        if arguments:
            try:
                self.process_arguments()
            except InvalidCommandError:
                print help_str
        else:
            if self.options.interactive is not None:
                self.c_menu()
            else:
                print help_str

    def printline(self, thick=True):
        if thick:
            print '=' * 79
        else:
            print '-' * 79

    def process_arguments(self, arguments=None):
        '''
        Process list of arguments. If 'arguments' is not given, use the arguments
        passed by the user when calling this script. 
        '''
        if arguments is None:
            arguments = self.arguments

        cmd = arguments.pop(0)
        try:
            cmd_f = getattr(self, 'c_' + cmd.replace('-', '_'))
        except AttributeError:
            print 'error: unknown command %s\n' % repr(cmd)
            raise InvalidCommandError
        cmd_f(*arguments)

    #===========================================================================
    # OBJECT CREATION
    #===========================================================================
    def new_json(self, schema, keys, values):
        '''Create JSON object from schema, keys and values. 
        
        Arguments
        ---------
        
        schema : Schema
            Schema used to validate and introspect data types in JSON object.
            
        keys : list of str
            List that defines the order that keys are read.
            
        values: list of str
            Values of the arguments.
        '''

        # Decorate list of arguments
        pretty_keys = [ key.title().replace('_', ' ') for key in keys ]
        json = dict(zip(keys, values))

        # Print all arguments that were set
        for key, pkey in zip(keys, pretty_keys):
            if key in json:
                print '    %s: %s' % (pkey, json[key])

        # Ask the user to complete the missing arguments
        for key, pkey in zip(keys[len(values):], pretty_keys[len(values):]):
            value = raw_input('    %s: ' % pkey)
            if value:
                json[key] = value

        # Check for bad entries
        bad_entry = True
        while bad_entry:
            bad_entry = False
            for k, v in json.items():
                sch = str(schema[k])
                if 'String' not in sch:
                    # Convert from Numbers
                    if 'Number' in sch or 'Integer' in sch:
                        try:
                            v = int(v)
                        except TypeError:
                            v = float(v)
                        json[k] = v

                    # Convert from Booleans
                    if 'Boolean' in sch:
                        try:
                            v = bool(int(v))
                        except ValueError:
                            v = {'t': True, 'f': False,
                                 'y': True, 'n': False,
                                 'yes': True, 'no': False,
                                 'true': True, 'false': False}[v.lower()]
                        json[k] = v

                # Attempt to validate each value.
                if not schema[k].is_valid(v):
                    new_entry = raw_input('Bad entry "%s=%s", type again: ' % (k, v))
                    if not new_entry:
                        del json[k]
                    else:
                        json[k] = v
                    bad_entry = True

        return json

    def new_obj(self, cls, keys, values, name=None):
        '''
        Creates a new object.
        
        
        Arguments
        ---------
        
        obj_name : str
            Object type's name
        
        schema : Schema
            Schema used to validate and introspect data types in JSON object.
            
        keys : list of str
            List that defines the order that keys are read.
            
        values: list of str
            Values of the arguments.
        '''
        if name is None:
            name = cls.__name__
        name, Name = name.lower(), name
        schema = cls.schema

        # Create equivalent JSON object
        print 'New %s:' % name
        json = self.new_json(schema, keys, values)

        # Hit the database...
        print
        print 'Creating...' % Name
        self.printline(False)
        #from tutor.db.course import Course
        obj = cls.from_keys(**json)
        obj.pprint()

        # Ask if user accepts the new object or not
        create = raw_input('\Save this %s? (y/n)' % name).lower()
        if create != 'y':
            obj.delete()
            print '%s deleted!' % Name
            return None
        else:
            obj.save()
            setattr(self, name, obj)
            print '%s created!' % Name
            return obj

    def c_new_course(self, *values):
        '''tutor new-course [arg1] [arg2] ...
        
        Create a new course. Additional arguments are interpreted as the fields 
        in the following order: course_id, title, lang, is_active, comment.
        The user will be queried for any missing fields.'''

        from tutor.db.course import Course
        keys = 'course_id title lang is_active comment'.split()
        self.new_obj(Course, keys, values)

    def c_new_classroom(self, *values):
        '''tutor new-classroom [arg1] [arg2] ...
        
        Create a new classroom. Additional arguments are interpreted as the fields 
        in the following order: course_id, title, lang, is_active, comment.
        The user will be queried for any missing fields.'''

        from tutor.db.course import Course
        keys = 'course_id title lang is_active comment'.split()
        self.new_obj(Course, keys, values)

    def c_new_student(self, *values):
        '''tutor new-student [arg1] [arg2] ...
        
        Create a new student. Additional arguments are interpreted as the fields 
        in the following order: school_id full_name email is_active.
        The user will be queried for any missing fields.'''

        from tutor.db.person import Person
        keys = 'school_id full_name email is_active'.split()
        student = self.new_obj(Person, keys, values, name='Student')
        if student is not None:
            student.role = 'student'
            student.save()

    #===========================================================================
    # OBJECTS DISPLAY
    #===========================================================================
    def list_generic(self, obj_cls, fields, fields_pretty=None, field_size=15):
        # Query objects
        objects = getattr(obj_cls, 'objects', obj_cls)
        objects = objects.all().order_by(fields[0])
        fields_v_list = objects.values_list(*fields)

        # Adjust size list and create accumulated sizes list
        try:
            sizes = iter(field_size)
        except TypeError:
            sizes = [ field_size ] * len(fields)
        accumulator, acc_sizes = 0, []
        for size in sizes:
            accumulator += size
            acc_sizes.append(accumulator)

        # Print table: head
        if fields_pretty is None:
            fields_pretty = [ f.title().replace('_', ' ') for f in fields ]
        head_str = ' #   '
        for L, f in zip(acc_sizes, fields_pretty):
            head_str = (head_str + f + ' ').ljust(4 + L)
        print '\n' + head_str
        self.printline(False)

        # Print table: body
        for (i, fields_v) in enumerate(fields_v_list):
            st = (' %s) ' % (i + 1)).ljust(5)
            for L, f in zip(acc_sizes, fields_v):
                st = (st + unicode(f) + ' ').ljust(4 + L)
            print st

        # Query user to select one object
        choice = raw_input('\nSelect object (ret. to go back): ')
        print
        if not choice:
            return None

        # Return object
        try:
            choice = int(choice)
            select_obj = objects[choice - 1]
            self.printline(False)
            print 'Selected object:\n'
            select_obj.pprint()
            raw_input('\n\npress ret. to continue...')
            return select_obj
        except (ValueError, KeyError, IndexError):
            print 'error: invalid choice, %s' % repr(choice)

    def c_list(self, whattype='courses'):
        '''tutor list <object>
        
        Print a list of all <object>s.
        '''
        method = getattr(self, 'c_list_%s' % whattype)
        return method()

    def c_list_courses(self):
        '''tutor list-courses
        
        Print a list of all courses.
        '''

        self.printline()
        print
        print 'List of Courses'
        from tutor.db.course import Course
        self.course = self.list_generic(Course, ['course_id', 'title', 'is_active'],
                                  ['ID', 'Title', 'Active'],
                                  [ 13, 40, 7])

        # Return to menu in interactive mode
        if self.options.interactive is not None:
            self.c_menu_list()

    def c_list_classes(self, course=None):
        '''tutor list-classes [course_id]
        
        Print a list of all classes. If the optional 'course_id' argument is given,
        it filters all classes of a given Course.
        '''

        self.printline()
        print
        print 'List of Classes'
        from tutor.db.classroom import Classroom

        # Filter classrooms by course, if necessary
        if course:
            from tutor.db.classroom import Course
            try:
                course = Course.objects.get(course_id=course)
            except Course.DoesNotExist:
                print 'Course does not exist: %s' % course
                return
            query = Classroom.objects.filter(course=course)
        else:
            query = Classroom.objects

        # Print list of classrooms
        self.list_generic(query, ['course__course_id', 'classroom_id', 'teacher__full_name', 'is_active'],
                                 ['Course', 'ID', 'Teacher', 'Active'],
                                 [ 13, 5, 25, 7])

        # Return to menu in interactive mode
        if self.options.interactive is not None:
            self.c_menu_list()

    def c_list_students(self):
        '''tutor list-students
        
        Print a list of all students.
        '''

        self.printline()
        print
        print 'List of Students'
        from tutor.db.person import Person
        role_no = Person._ROLE2NO['student']
        query = Person.objects.filter(role_no=role_no)
        self.list_generic(query, ['school_id', 'full_name', 'is_active'],
                                  ['ID', 'Name', 'Active'],
                                  [ 13, 40, 7])

        # Return to menu in interactive mode
        if self.options.interactive is not None:
            self.c_menu_list()

    def c_list_activities(self):
        '''tutor list-activities
        
        Print a list of all activities.
        '''

        self.printline()
        print
        print 'List of Activities'
        from tutor.db.activity import Activity
        query = Activity.objects.all()
        self.list_generic(query, ['_classroom', 'exam__title', 'is_active'],
                                 ['Classroom', 'Exam', 'Active'],
                                 [ 20, 30, 7])

        # Return to menu in interactive mode
        if self.options.interactive is not None:
            self.c_menu_list()

    def c_list_tasks(self):
        '''tutor list-tasks
        
        Print a list of all tasks.
        '''

        self.printline()
        print
        print 'List of Tasks'
        from tutor.db.task import Task
        query = Task.objects.all()
        self.list_generic(query, ['student__full_name', '_activity__exam__title', 'is_active'],
                                 ['Student', 'Exam', 'Active'],
                                 [ 25, 25, 7])

        # Return to menu in interactive mode
        if self.options.interactive is not None:
            self.c_menu_list()

    #===========================================================================
    # HELP
    #===========================================================================
    def c_help(self, arg):
        '''tutor help <command>
        
        Prints additional help on specific <command>.'''

        arg = arg.replace('-', '_')
        docstring = getattr(self, 'c_%s' % arg).__doc__.splitlines()
        print '\n'.join(l.strip() for l in docstring)


    #===========================================================================
    # MENU
    #===========================================================================
    def c_menu(self, menuitem=None):
        '''tutor menu [menuitem]
        
        Display an interactive menu with options. The optional menuitem argument
        can be either 'list', 'new', 'del', 'edit', 'action'. If given, it prints
        the menu associated with the given option. This form   
        '''
        if menuitem:
            cmd = 'menu-' + menuitem
            return self.process_arguments(cmd)

        # Print options
        self.printline()
        print
        print 'SELECT ONE OF THESE OPTIONS'
        print
        print ' 1) Select/display objects'
        print ' 2) Create objects'
        print ' 3) Delete objects'
        print ' 4) Edit objects'
        print ' 5) Actions'
        print
        opt = raw_input('Choose option: ')

        # Choose the right command to be issued
        try:
            opt = int(opt)
            cmd = { 1: 'menu-list',
                    2: 'menu-new',
                    3: 'menu-del',
                    4: 'menu-edit',
                    5: 'menu-action'}[opt]
        except (ValueError, KeyError):
            cmd = opt

        # Tries to execute command
        try:
            print
            self.process_arguments([cmd])
        except InvalidCommandError:
            time.sleep(0.75)
            self.c_menu()

    def make_menu(self, options):
        self.printline()
        print
        print 'SELECT TYPE'
        print
        cmd = {}
        for (i, (n, v)) in enumerate(options):
            cmd[i + 1] = v
            print ' %s) %s' % (i + 1, n)
        print
        opt = raw_input('Choose option (ret. to go back): ')
        if not opt:
            self.c_menu()

        # Choose the right command to be issued
        try:
            opt = int(opt)
            cmd = cmd[opt]
            print
            self.process_arguments([cmd])
        except (ValueError, KeyError):
            time.sleep(0.75)
            print 'error: invalid option %s' % repr(opt)
        except InvalidCommandError:
            time.sleep(0.75)
            self.c_menu()

    def c_menu_list(self):
        '''tutor menu-list
        
        Display an interactive menu to choose which kind of objects should be
        listed.   
        '''
        names = 'Courses Classes Students Activities Tasks'.split()
        values = [ 'list-%s' % x.lower() for x in names ]
        options = list(zip(names, values))
        self.make_menu(options)

    def c_menu_new(self):
        '''tutor menu-new
        
        Display an interactive menu to choose which kind of objects should be
        created.   
        '''
        names = 'Course Classroom Student Activity Task'.split()
        values = [ 'new-%s' % x.lower() for x in names ]
        options = list(zip(names, values))
        self.make_menu(options)

    def c_menu_del(self):
        '''tutor menu-del
        
        Display an interactive menu to choose which kind of objects should be
        deleted.   
        '''
        names = 'Course Classroom Student Activity Task'.split()
        values = [ 'del-%s' % x.lower() for x in names ]
        options = list(zip(names, values))
        self.make_menu(options)

    def c_menu_edited(self):
        '''tutor menu-del
        
        Display an interactive menu to choose which kind of objects should be
        edited.   
        '''
        names = 'Course Classroom Student Activity Task'.split()
        values = [ 'edit-%s' % x.lower() for x in names ]
        options = list(zip(names, values))
        self.make_menu(options)


def main():
    # Configure optparse
    p = optparse.OptionParser(description='Control the tutor system. Use %prog --help option to ',
                              prog='tutor',
                              version='tutor ' + settings.VERSION,
                              usage='%prog [option] [args] command')
    p.add_option('--interactive', '-i', help='enable interactive mode', action='store_false')
    options, arguments = p.parse_args()

    # Create help string
    cmd_list = [ '  ' + c[2:].replace('_', '-') for c in dir(Task) if c.startswith('c_') ]
    cmd_list = '\n'.join(sorted(cmd_list))
    F = StringIO()
    p.print_help(F)
    help_str = F.getvalue() + '\nAvailable commands:\n%s' % cmd_list

    # Execute task
    Task(options, arguments, help_str=help_str)

if __name__ == '__main__':
    #from tutor.db.person import Person
    #from pprint import pprint
    main()
