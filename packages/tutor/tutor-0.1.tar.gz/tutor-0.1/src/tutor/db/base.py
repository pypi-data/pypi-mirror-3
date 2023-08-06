import json
import os
import sys
from cStringIO import StringIO
import tutor.db
from django import forms
from django.db import models
from django.db.models import *
from django.template import Template, Context
from tutor.util.json_to_django import ToDjango
from tutor.config import settings
__all__ = [ 'Printable', 'ORMModel' ]

#===============================================================================
#                        METHODS FOR PRINTING OUTPUT
#===============================================================================
class Printable(object):
    def pretty(self, display_empty=False, **kwds):
        '''
        Pretty-print representation of object.
        
        Arguments
        ---------
        
        display_empty : bool
            If True, it will display empty fields in JSON object. The default
            behavior is to omit these fields if they are equal to the default
            or null value.
        
        '''

        try:
            return self.print_trasformation('pretty', **kwds)
        except IOError:
            keys = self.schema.fields
            active = getattr(self, 'is_active', True)
            active = (' (inactive)' if not active else '')
            header = "[ %s '%s'%s ]" % (type(self).__name__,
                                        getattr(self, keys[0]),
                                        active)
            pretty = [ header ]
            pretty_tail = []

            # Process each key
            for k in keys[1:]:
                # 'is_active' already appears in the header section
                if k == 'is_active':
                    continue

                # Get value for current key
                try:
                    value = kwds[k]
                except KeyError:
                    value = getattr(self, k)

                # Choose to display it or not
                if not value:
                    if display_empty:
                        value = '---'
                    else:
                        continue

                # If value is an array, prints it in a nice well-formatted way
                kwds['display_empty'] = display_empty
                if isinstance(value, (list, tuple)):
                    values = [ '\n    [ %s ]' % k.title() ]
                    for item in value:
                        try:
                            item = item.pretty(**kwds)
                            item = '\n      '.join(item.splitlines())
                            item = unicode('       ' + item)
                        except AttributeError:
                            item = u'       * %s' % item
                        values.append(item)
                    pretty_tail.append('\n'.join(values))
                else:
                    pretty.append('    %s: %s' % (k, unicode(value)))
            return '\n'.join(pretty + pretty_tail)

    def pprint(self, coding='utf8', **kwds):
        '''Pretty-print object'''
        print(self.pretty(**kwds).encode(coding))

    def latex(self, **kwds):
        '''
        Latex representation of object.
        '''
        # Possible plastex bug? fix spurious spacings 
        ret = self.print_trasformation('latex', **kwds)
        ret = ret.replace('} ~ ', '}~')
        ret = ret.replace(' ~ {', '~{')
        return ret

    def latex_document(self, **kwds):
        '''
        Like obj.latex(), but creates a full latex document.
        '''

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
               '\\usepackage{auto-pst-pdf,pst-barcode,pstricks-add}\n\n'\
               '\\providecommand{\\tabularnewline}{\\\\}'\
               '\\begin{document}\n\n'
        tail = u'\n\n\\end{document}'

        if kwds.get('_split_sections', False):
            return head, tail
        else:
            return head + self.latex(**kwds) + tail

    def xhtml(self):
        return self.print_trasformation('xhtml', **kwds)

    def print_trasformation(self, transformation, template_name=None, **kwds):
        # Transform JSON representation using rule.
        json = { 'self': self }
        for k in sorted(self.schema):
            obj = getattr(self, k)
            try:
                func = getattr(obj, transformation)
            except AttributeError:
                func = None
            if func is not None:
                obj = func(**kwds)
            json[k] = obj

        # Find template corresponding to object.
        if template_name is None:
            class_name = type(self).__name__.lower()
            template_name = '{0}_{1}'.format(class_name, transformation)
        base = settings.TEMPLATE_DJANGO_TEMPLATE_PATH
        tpath = os.path.join(base, template_name) + '.dat'

        try:
            template = settings.LOADED_TEMPLATES[tpath]
        except KeyError:
            with open(tpath) as F:
                template = F.read()
            template = Template(template)
            settings.LOADED_TEMPLATES[tpath] = template

        # Render template.
        c = Context(json)
        return unicode(template.render(c))

    def save_pdf(self, **kwds):
        # link all files in media to tmp
        media_files = os.listdir(settings.TEMPLATE_MEDIA_PATH)
        linked_files = os.listdir(settings.TEMPLATE_TMP_PATH)
        for file in media_files:
            if not file in linked_files:
                media = os.path.join(settings.TEMPLATE_MEDIA_PATH, file)
                link = os.path.join(settings.TEMPLATE_TMP_PATH, file)
                os.link(media, link)

        # creates latex file and compile to pdf
        self.save_latex(**kwds)
        filename = self.name.replace('::', '__').replace('/', '__').replace(' ', '_')
        working_dir = os.getcwd()
        try:
            os.chdir(settings.TEMPLATE_TMP_PATH)
            try:
#                old_std = sys.stderr, sys.stdin, sys.stdout
#                sys.stderr = sys.stdin = sys.stdout = new_std = StringIO()
                cmd = 'pdflatex --shell-escape "%s.tex" 12> last_job.log' % filename
                os.system(cmd)
            finally:
                pass
#                sys.stderr, sys.stdin, sys.stdout = old_std
#                data = new_std.read()
#                if data:
#                    data = '\n' + '-' * 80 + data
#                    with open('last_job.log', 'a') as F:
#                        F.write(data)

            # save a copy at last_job.pdf
            with open('%s.pdf' % filename, 'r') as F1:
                with open('last_job.pdf', 'w') as F2:
                    F2.write(F1.read())
        finally:
            os.chdir(working_dir)

    def save_latex(self, **kwds):
        filename = self.name.replace('::', '__').replace('/', '__').replace(' ', '_') + '.tex'
        path = os.path.join(settings.TEMPLATE_TMP_PATH, filename)
        tex = self.latex_document(**kwds)
        with open(path, 'w') as F:
            F.write(tex)

#===============================================================================
#                                 ORMModel
#===============================================================================
class ORMBaseModel(Printable):
    @classmethod
    def format_keys(cls, *args, **kwds):
        fields = cls.schema.fields
        kwds.update(dict(zip(fields, args)))

        # Check if all keys are good
        kwds_set = set(kwds)
        if not kwds_set.issubset(cls.init_keys):
            bad_keys = iter(kwds_set - cls.init_keys)
            raise TypeError('bad key: %s' % repr(bad_keys.next()))
        return kwds

    @classmethod
    def from_keys(cls, *args, **kwds):
        kwds = cls.format_keys(*args, **kwds)
        db_fields = {}

        for f in cls.db_fields:
            try:
                db_fields[str(f)] = kwds.pop(f)
            except KeyError:
                pass

        # Adjust reference fields
        for f in cls.db_references:
            value = db_fields.get(f, None)
            if not (isinstance(value, cls) or value is None):
                db_fields[f + '_id'] = db_fields.pop(f)

        new = cls(**db_fields)
        for k, v in kwds.items():
            # Test if property is a json_property
            prop_type = type(getattr(cls, k))
            if prop_type is ToDjango.json_property:
                new._json[k] = v
            else:
                setattr(new, k, v)
        new.pre_save()
        new.save()
        return new

    @classmethod
    def from_json(cls, json, save_backup=False, load_backup=False):
        new = None
        if load_backup:
            try:
                new = cls.from_backup(json[cls._meta.pk.name])
                for k, v in json.items():
                    setattr(new, k, v)
            except IOError:
                pass

        if new is None:
            kwds = dict((str(k), v) for (k, v) in json.items())
            new = cls.from_keys(**kwds)

        if save_backup:
            new.save_backup()
        return new

    @classmethod
    def from_lib(cls, addr, try_pk=False, reload=False, **kwds):
        """Load object located at 'addr' in tutor lib. 
        
        
        #TODO: ?? If an object with name
        equal to 'addr' already exists, the files in tutor lib are tested for 
        changes. If no changes are detected, it simply return the latest version
        of the template object. Otherwise, it creates a new version and append
        a versioning number to its name. ??
        
        Arguments
        ---------
        
        addr : str
            Location of template in the template database.    
        
        Output
        ------
        
        The ORMModel object that represents the template.    
        """

        if not reload:
            try:
                return cls.objects.get(pk=addr)
            except cls.DoesNotExist as ex:
                if try_pk and '::' in addr:
                    raise ex

        mod_path = 'tutor.lib.loaders.%s' % cls._lower_name
        M = __import__(mod_path, fromlist=['from_addr'])
        json_obj = M.from_addr(addr, validate=False, **kwds)

        # json_obj may be a list of objects or a single object
        if isinstance(json_obj, (list, tuple)):
            obj_list = []
            for obj in json_obj:
                obj_list.append(cls.from_json(obj, **kwds))
            return obj_list
        else:
            return cls.from_json(json_obj, **kwds)

    @classmethod
    def from_backup(cls, name, **kwds):
        addr = cls.backup_path(name)
        with open(addr) as F:
            json_obj = json.load(F)
        kwds['load_backup'] = False
        return cls.from_json(json_obj, **kwds)

    @classmethod
    def backup_path(cls, name=None):
        if name is None:
            return os.path.join(settings.LIB_BACKUP, cls._lower_name)
        else:
            addr = os.path.join(cls._lower_name, name.replace('/', '>') + '.json')
            return os.path.join(settings.LIB_BACKUP, addr)

    @classmethod
    def save_backup_all(cls, human_readable=True, rewrite=False):
        if rewrite:
            for obj in cls.objects.all():
                obj.save_backup(human_readable=human_readable)
        else:
            files = (os.path.splitext(f)[0] for f in cls.backup_listfiles())
            files = set(f.replace('>', '/') for f in files)
            pk = cls._meta.pk.name
            for obj_pk in cls.objects.all().values_list(pk, flat=True):
                if not obj_pk in files:
                    obj = cls.objects.get(**{ pk: obj_pk })
                    obj.save_backup()

    @classmethod
    def get_json_backup_all(cls):
        backup_dir = cls.backup_path()
        for f in cls.backup_listfiles():
            full_path = os.path.join(backup_dir, f)
            with open(full_path) as F:
                yield json.load(F)

    @classmethod
    def load_backup_all(cls, rewrite=False):
        pk = cls._meta.pk.name
        for json in cls.get_json_backup_all():
            try:
                obj = cls.objects.get(**{pk: json[pk]})
                if rewrite:
                    obj.json_update(json)

            except cls.DoesNotExist:
                cls.from_json(json)

    @classmethod
    def backup_listfiles(cls):
        addr = cls.backup_path()
        return os.listdir(addr)

    def save_backup(self, human_readable=True):
        indent = (4 if human_readable else None)
        with open(self.backup_path(self.pk), 'w') as F:
            json.dump(self.json(), F, indent=indent, encoding='utf8')

    def get_json_backup(self):
        with open(self.obj_lib_path()) as F:
            try:
                return json.load(F, encoding='utf8')
            except IOError:
                return None

    def validate(self):
        self.schema.validate(self.json)

    def pre_save(self):
        '''
        Execute before saving object
        '''
        pass

    def filled_items(self, raw=True, keys=None, values=None):
        if keys and values:
            raise ValueError('cannot set keys and values simultaneously')

        items = self._filled_items_generator()
        if keys:
            for (k, v, f) in items :
                yield k
        elif values and raw:
            for (k, v, f) in items :
                yield v
        elif values:
            for (k, v, f) in items :
                if f:
                    yield getattr(self, k)
                else:
                    yield v
        elif raw:
            for (k, v, f) in items :
                yield (k, v)
        else:
            for (k, v, f) in items :
                if f:
                    yield (k, getattr(self, k))
                else:
                    yield (k, v)

    def _filled_items_generator(self):
        cls = type(self)
        schema = self.schema
        for k, sch in schema.items():
            if k in self.db_references:
                value = getattr(self, k + '_id')
                if value is not None:
                    yield (k, value, True)
            elif k in self.db_fields:
                value = getattr(self, k)
                if value != sch.default_or_null:
                    yield (k, value, False)
            else:
                prop_type = type(getattr(cls, k))
                if prop_type is ToDjango.json_property:
                    if k in self._json:
                        value = self._json[k]
                        yield (k, value, True)
                else:
                    value = getattr(self, k)
                    if value != sch.default_or_null:
                        yield (k, value, False)

    def json(self, raw=True):
        '''
        Convert object to its JSON representation.
        
        
        Arguments
        ---------
        
        raw : bool
            If False, the resulting structuture can hold arbitrary Python 
            objects. Otherwise everything is converted to valid JSON. 
        '''

        return dict((unicode(k), v) for (k, v) in self.filled_items(raw=raw))

    def json_update(self, json):
        for (k, v) in json:
            if k in self.db_references and not isinstance(v, ORMModel):
                k = k + '_id'
            setattr(self, k, v)

class ORMModel(ORMBaseModel):
    class __metaclass__(type):
        models = {}

        def __new__(cls, name, bases, dic):
            # Avoid creating the same model twice
            try:
                ORMModel
                return cls.models[name]
            except NameError:
                return type.__new__(cls, name, bases, dic)
            except KeyError:
                schema = dic['schema']

            # Fix app_label and create temporary type
            try:
                dic['Meta'].app_label = 'orm'
            except KeyError:
                class Meta:
                    app_label = 'orm'
                dic['Meta'] = Meta

            # Remove ORMModel from bases to avoid conflict with Django's 
            # models metaclass
            bases = list(bases)
            del bases[bases.index(ORMModel)]
            bases.extend(ORMModel.mro()[1:])
            bases = tuple(bases)

            # Lower-case version of name
            last_islower = False
            lower_name = []
            for c in name:
                islower = c.islower()
                if last_islower and (not islower):
                    lower_name.append('_')
                last_islower = islower
                lower_name.append(c.lower())
            dic['_lower_name'] = ''.join(lower_name)

            # Register db_fields, serialized_fields and init_keys
            fields = set(schema)
            db_fields = set(dic.get('db_fields', ()))
            serialized_fields = set(dic.get('serialized_fields', ()))
            if db_fields and serialized_fields:
                raise TypeError("cannot define 'db_fields' and 'serializable_fields' simultaneously")
            elif db_fields:
                serialized_fields = fields - db_fields
            else:
                db_fields = fields - serialized_fields
            if not db_fields.issubset(schema):
                f = iter(db_fields - set(schema))
                raise ValueError('invalid field: %s' % repr(f.next()))

            dic['db_fields'] = db_fields
            dic['serialized_fields'] = serialized_fields
            dic.setdefault('init_keys', set(schema.keys()))
            dic['init_keys'] = set(dic['init_keys'])

            # Return django-enabled type
            conv = ToDjango(type.__new__(cls, name, bases, dic), db_fields=db_fields)
            new = conv.subtype()

            # Register reference fields
            new.db_references = set()
            for field in new._meta.fields:
                if isinstance(field, models.ForeignKey):
                    new.db_references.add(field.name)

            return new

class HasChildren(object):
    @property
    def template(self):
        if self.is_template:
            return self
        else:
            template = self.parent
            if template.is_template:
                return template
            else:
                raise ValueError('invalid template')

    @classmethod
    def from_template(cls, template):
        '''
        Return an object from a given template under 'addr'.
        
        
        Arguments
        ---------
        
        template : ORMObject or str
            Template object or the location of template in tutor lib.
            
        '''

        if isinstance(template, basestring):
            try:
                template = cls.objects.get(template_name=template, is_template=True)
            except cls.DoesNotExist:
                template = cls.from_lib(template)
        return template.child()

    def child(self, **kwds):
        """Creates a new child.
        
        Output
        ------
        
        'ORMObject' object generated using the current template.
        
        """


        # Check if self is a valid parent        
        if not self.is_template:
            if self.parent_id is None or not self.parent.is_template:
                raise TypeError('not a valid template')
            else:
                return self.parent.new_child(**kwds)

        # Create children with same db_fields
        child = type(self)()
        for field in self.db_fields:
            if hasattr(self, field):
                setattr(child, field, getattr(self, field))
        child.parent = self
        child.is_template = False

        # Update _json field, if it exists
        try:
            child._json = json.loads(json.dumps(self._json))
        except AttributeError:
            pass

        # Check if pk is a string and update pk accordingly
        if isinstance(self._meta.pk, (models.CharField, models.TextField)):
            fname = self._meta.pk.name
            pk_value = getattr(self, fname)
            query = type(self).objects.filter(**{'%s__startswith' % fname: pk_value})
            query = query.filter(**{'%s__contains' % fname: '::'})
            pk_values = query.values_list(fname, flat=True)
            values = set(int(n.rpartition('::')[2]) for n in pk_values)
            for i in range(len(values) + 1):
                if not i in values:
                    new_pk_value = u'{0}::{1}'.format(pk_value, i)
                    setattr(child, fname, new_pk_value)
                    break

        # Return saved object
        if kwds.get('_save', True):
            if kwds.get('_pre_save', True):
                child.pre_save()
            child.save()
        return child
