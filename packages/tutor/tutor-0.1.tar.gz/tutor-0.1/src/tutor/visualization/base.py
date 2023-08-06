#-*- coding: utf8 -*-
from tutor import SETTINGS
from tutor.config import schemas
from tutor.data.media_files import MEDIA_FILES
from tutor.util.jsonlib import all as jsonlib
from tutor.util.django import template as django_template
import copy
import functools
import os
import sys
import tempfile

try:
    TEMPLATES_PATH = SETTINGS['Templates']['path']
except KeyError:
    TEMPLATES_PATH = os.path.join(SETTINGS['Tutor']['root_path'], 'templates')

class Visualization(object):
    def __init__(self):
        '''
        Classes that create useful visualizations for data. It can be used
        to generate useful pretty-print visualization to formatting using, e.g.,
        LaTeX. 
        '''
        self._transformations = []

        for fname in dir(self):
            # Automatic key transformations
            if fname.startswith('key_T_'):
                key = fname[6:]
                func = getattr(self, fname)
                self.add_key_transformation(key, func)

            # Automatic transformations
            elif fname.startswith('T_'):
                func = getattr(self, fname)
                self.add_transformation(func)

            # Automatic array transformations
            elif fname.startswith('array_T_'):
                key = fname[8:]
                func = getattr(self, fname)
                self.add_array_transformation(key, func)

    def add_transformation(self, T, name=None):
        '''
        Adds a transformation T to the transformations list. The signature of
        T() is  T(JSON-like) -> JSON-like.
        '''
        if name is None:
            name = 'T<%s>' % len(self._transformations)
        self._transformations.append((name, T))

    def add_key_transformation(self, key, T, name=None):
        '''
        Adds a transformation T that acts only on a key of a JSON-like object.
        The signature of T() is  T(JSON-like) -> JSON-like.
        '''
        def transform(key, obj):
            try:
                value = obj[key]
            except KeyError:
                return obj
            else:
                obj[key] = T(value)
                return obj

        if name is None:
            name = 'keyT<%s>' % key
        self.add_transformation(functools.partial(transform, key), name=name)

    def add_array_transformation(self, key, T, itemize=False, name=None):
        '''
        Transform each element in an array at given key by the transformation T.
        
        If itemize is True, assumes that object in 'key' is a dictionary, and 
        T is a function that receives a (key, value) pair as input. The result
        of the transformation is, however, always an array build with the 
        output of T.
        '''
        def safe_T(*args):
            try:
                return T(*args)
            except Exception as ex:
                return 'invalid T(%s): %s' % (', '.join(map(str, args)), ex)

        if itemize:
            def transform(T, obj):
                return [ T(k, v) for (k, v) in itemize(obj) ]
        else:
            def transform(T, obj):
                return [ T(item) for item in obj ]

        if name is None:
            name = 'arrayT<%s>' % key

        self.add_key_transformation(key, functools.partial(transform, safe_T), name=name)

    def block_keys(self, *keys):
        '''
        Discard key when building visualization for given object.
        '''
        def del_key(keys, obj):
            for key in keys:
                if key in obj:
                    del obj[key]
            return obj
        self.add_transformation(functools.partial(del_key, keys), 'delT<%s>' % (', '.join(keys)))

    def prepare_input(self, obj):
        '''
        Prepares object to be rendered. If Visualization has set any
        transformation, they will be applied to object at this stage. 
        '''
        if self._transformations:
            obj = jsonlib.copy(obj)
            for name, T in self._transformations:
                try:
                    obj = T(obj)
                except Exception as ex:
                    print('error caught in transformation %s: %s' % (name, ex))
#                    break
        return obj

    def render(self, obj):
        raise NotImplementedError

    def dump(self, obj, file=sys.stdout):
        '''
        Dumps a visualization data that represents a given JSON-like 
        structure 'obj' into 'file'. If not file is given, it prints the 
        visualization on screen
        '''
        if isinstance(file, basestring):
            with open(os.path.expanduser(file), 'w') as F:
                F.write(self.render(obj))
        else:
            file.write(self.render(obj))

#===============================================================================
#                     Access to templates library
#===============================================================================
class HasTemplate(Visualization):
    LOADED_TEMPLATES = {}

    def __init__(self):
        super(HasTemplate, self).__init__()
        self._vis_mapping = {}

    def _render(self, obj, template):
        '''
        Loads and renders object using a given template 
        '''
        base = TEMPLATES_PATH
        tpath = os.path.join(base, template) + '.dat'

        try:
            template = self.LOADED_TEMPLATES[tpath]
        except KeyError:
            with open(tpath) as F:
                template = F.read()
            template = django_template.Template(template)
            self.LOADED_TEMPLATES[tpath] = template

        c = django_template.Context(obj)
        return unicode(template.render(c))

    def render(self, obj):
        '''
        Returns a visualization string that represents a given JSON-like 
        structure 'obj'. 
        '''
        # Infer template _name from class _name
        obj = self.prepare_input(obj)
        name = type(self).__name__[:-len('Visualization')]
        name = (''.join((c if c.islower() else '_' + c.lower()) for c in name))
        if name.startswith('_'):
            name = name[1:]
        template = '_'.join(reversed(name.split('_')))
        return self._render(obj, template)


#===============================================================================
#                            Pretty printers
#===============================================================================
class Pretty(HasTemplate):
    def __init__(self, name=None, keys=[], header=None):
        '''
        Pretty-print representation of object.
        
        Arguments
        ---------
        
        name : str
            Name of the object
        keys : sequence
            Sequence with the order on keys should be displayed by the pretty
            printer 
        header : str
            String rendered to be the header section of the object display.
            The input object is passed to the .format() method of this string
            before actually building the final string to be rendered.
        '''
        super(Pretty, self).__init__()
        if name is None:
            name = type(self).__name__
            if name == 'Pretty':
                name = 'Generic Object'
            elif name.startswith('Pretty'):
                name = name[6:]
        self._keys = list(keys)
        self._shadow_keys = set()
        self._name = name
        self._header = header

        self.block_keys('is_active', '_name')

    def T_header(self, obj):
        'Header transformation: consolidate _name/type and is_active'

        if self._header is None:
            active = obj.get('is_active', True)
            active = (' (inactive)' if not active else '')
            header = "[ %s %s%s ]" % (self._name, obj.get('name', ''), active)
        else:
            header = self._header
        obj['__header__'] = header
        return obj

    def ommit_keys(self, *keys):
        'Prints only the contents of key, but do not print the key itself'
        for k in keys:
            self._shadow_keys.add(k)

    def move_to_tail(self, key):
        '''
        Move the given key to be the last object to be visualized
        '''

        keys = self._keys
        try:
            keys.pop(keys.index(key))
        except IndexError:
            pass
        keys.append(key)

    def _key_value_T(self, obj):
        k, v = obj
        return '%s: %s' % (k, str(v))

    def itemize_array(self, key, title=None, itemize=False):
        if itemize:
            def T(k, v):
                v = '\n    '.join(unicode(v).splitlines())
                return u'  %s: %s' % (unicode(k), v)
        else:
            def T(x):
                x = '\n    '.join(unicode(x).splitlines())
                return u'  * %s' % x

        def key_T(title, array):
            if title is None:
                title = '\n[ %s ]' % key.replace('_', ' ').title()
            data = '\n'.join(array)
            data = '%s\n%s' % (title, data)
            return data

        self.add_array_transformation(key, T, itemize=itemize)
        self.add_key_transformation(key, functools.partial(key_T, title))
        self.ommit_keys(key)

    def render(self, obj, display_empty=False):
        '''
        Renders object with a nice pretty print representation
        '''

        obj = self.prepare_input(obj)

        pretty = [obj.pop('__header__')]
        pretty_tail = []
        o_keys, keys = set(obj.keys()), []
        for k in self._keys:
            o_keys.discard(k)
            keys.append(k)
        keys.extend(o_keys)
        for k in keys:
            # Get key and choose to display it or not
            value = obj.get(k, None)
            if not value:
                if display_empty:
                    value = '---'
                else:
                    continue

            if k in self._shadow_keys:
                value = '\n  '.join(unicode(value).splitlines())
                pretty.append('  %s' % value)
            else:
                value = '\n    '.join(unicode(value).splitlines())
                pretty.append('  %s: %s' % (k, value))

        return '\n'.join(pretty + pretty_tail)

# Pretty printer types ---------------------------------------------------------

#===============================================================================
#                     Generic Node Visualization
#===============================================================================
class NodeVisualization(Visualization):
    def __init__(self, cls, keys=['name', 'keys']):
        Visualization.__init__(self)
        if not isinstance(cls, dict):
            cls = { 'multiple-choice': cls,
                    'true-false': cls,
                    'association': cls,
                    'text': cls }

        # Support for different node types
        s = schemas
        for sch in [ s.MultipleChoice, s.TrueFalse, s.Association, s.Text ]:
            tex_name = sch['type'].default
            name = tex_name.replace('-', '_')
            kwds = dict(name=name, keys=sch.fields, tex_name=tex_name)
            for k in kwds.keys():
                if k not in keys:
                    kwds.pop(k)
            setattr(self, 'node_%s' % name, cls[tex_name](**kwds))

#        for node_vis_name in [ m for m in dir(self) if m.startswith('node')]:
#            node_vis = getattr(self, node_vis_name)
#            if 'items' in node_vis.keys:
#                item_renderer = getattr(self, 'render_%s_item' % node_vis_name)
#                node_vis.add_array_transformation('items', item_renderer)

    def render_multiple_choice(self, item):
        return self.node_multiple_choice.render(item)

    def render_true_false(self, item):
        return self.node_true_false.render(item)

    def render_association(self, item):
        return self.node_association.render(item)

    def render(self, obj):
        return getattr('render_%s_item' % (obj['type'].replace('-', '_')))(obj)

#===============================================================================
#                            LaTeX printing
#===============================================================================
class Tex(HasTemplate):
    head = u'\\documentclass[11pt,brazil,twoside]{article}\n'\
       '\\usepackage[T1]{fontenc}\n'\
       '\\usepackage[utf8]{inputenc}\n'\
       '\\usepackage[a4paper]{geometry}'\
       '\\geometry{verbose,tmargin=2cm,bmargin=2cm,lmargin=1.5cm,rmargin=1.5cm}\n'\
       '\\usepackage{amsmath}\n'\
       '\\usepackage{amssymb}\n'\
       '\\usepackage{array}\n'\
       '\\usepackage{graphicx}\n'\
       '\\usepackage{babel}\n'\
       '\\usepackage{esint}\n'\
       '\\usepackage{nopageno}\n'\
       '\\usepackage{enumitem}\n'\
       '\\usepackage{longtable}\n'\
       '\\usepackage{units}\n'\
       '\\usepackage{auto-pst-pdf,pst-barcode,pstricks-add}\n\n'\
       '\\providecommand{\\tabularnewline}{\\\\}'\
       '\\def\\sp{ }'\
       '\\begin{document}\n\n'
    tail = u'\n\n\\end{document}'

    def __init__(self, template, is_document=True):
        super(Tex, self).__init__()
        self.is_document = is_document
        self.template = template

    def _document(self, doc_body):
        return '%s\n%% Begin document\n%s\n%% End document\n %s' % \
            (self.head, doc_body, self.tail)

    def render(self, obj):
        obj = self.prepare_input(obj)
        doc_body = self._render(obj, self.template)
        if self.is_document:
            rendered = self._document(doc_body)
        else:
            rendered = doc_body

        rendered = rendered.replace('} ~ ', '}~')
        rendered = rendered.replace(' ~ {', '~{')
        return rendered

#===============================================================================
#                             PDF printing
#===============================================================================
class Pdf(Visualization):
    def __init__(self, tex_vis):
        self.to_tex = tex_vis
        if not self.to_tex.is_document:
            self.to_tex = copy.copy(self.to_tex)
            self.to_tex.is_document = True

    def render(self, obj):
        texfile = tempfile.NamedTemporaryFile('w', suffix='.tex')
        texfile_path = os.path.abspath(texfile.name)
        texfile_name = os.path.splitext(os.path.basename(texfile_path))[0]
        texfile_dir = os.path.dirname(texfile_path)
        with texfile:
            self.to_tex.dump(obj, texfile)
            texfile.flush()

            # Extract all media files from $TUTOR/lib/media
            for fname, abspath in MEDIA_FILES.items():
                fname = os.path.join(texfile_dir, fname)
                if not os.path.exists(fname):
                    os.symlink(abspath, fname)
#            # link all files in media to tmp
#            linked_files = os._listdir(settings.TEMPLATE_TMP_PATH)
#            for file in media_files:
#                if not file in linked_files:
#                    media = os.path.join(settings.TEMPLATE_MEDIA_PATH, file)
#                    link = os.path.join(settings.TEMPLATE_TMP_PATH, file)
#                    os.link(media, link)
            #...

            # Create pdf
            working_dir = os.getcwd()
            try:
                os.chdir(texfile_dir)
                try:
                    cmd = 'pdflatex --shell-escape "%s.tex" 12> tex_to_pdf_job.log' % texfile_name
                    os.system(cmd)
                    with open(texfile_name + '.pdf') as F:
                        pdfdata = F.read()
                finally:
                    # Delete temporary latex files
                    for suffix in [ '.log', '.aux', '-autopp.log' ]:
                        fname = texfile_name + suffix
                        if os.path.exists(fname):
                            os.unlink(fname)
            finally:
                os.chdir(working_dir)
        return pdfdata



