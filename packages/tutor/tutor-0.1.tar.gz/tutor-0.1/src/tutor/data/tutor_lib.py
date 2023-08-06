from tutor.data import conversions
from tutor.data.raw_lib import LibNode
from tutor.config.schemas import LearningObj, Exam, MultipleChoice, TrueFalse, Association, Text
from tutor.util.jsonlib import all as jsonlib

__all__ = [ 'get_learning_obj', 'get_exam']

class LibTemplate(object):
    #TODO: desmembrar classe/transpor parte da logica para raw_data

    # Importers
    learning_obj_main_import = conversions.learning_obj.MainImport()
    learning_obj_names_import = conversions.learning_obj.NamesImport()
    exam_main_import = conversions.exam.MainImport()

    # Validators
    NODE_VALIDATOR = staticmethod(
        lambda x: { 'multiple-choice': MultipleChoice,
                    'true-false': TrueFalse,
                    'association': Association,
                    'text': Text}[x['type']])

    LOBJ_VALIDATOR = staticmethod(lambda x: LearningObj)

    def get_template(self, name, validate=True):
        type, _, name = name.partition('/')
        loader = getattr(self, 'template_%s' % type)
        return loader(name, validate)

    def get_learning_obj_template(self, name, validate=True):
        '''
        Get the JSON representation of a Learning Object template. 
        
        Parameters
        ----------  
        name : str
            An address in the library
        validate : bool
            If True, checks if the output is valid.
            
        Output
        ------
        A JSON-like object representing the Learning Object template.
        '''
        new, node = self._get_main(name, 'learning_obj', self.learning_obj_main_import)

        # Builds namespace (if present)
        if 'names' in node.sections:
            with node.open('names') as F:
                namespace = self.learning_obj_names_import.load(F, F.type)
            new[u'namespace_pool'] = namespace

            # Build name substitutions
            new[u'namespace_subs'] = jsonlib.get_subs(
                new, braces=('||', '||'),
                escape=(r'\||', r'\||'),
                filter_fmt=jsonlib.filter_fmt_math
            )

            # Construct list of variables if necessary
            varnames = new['namespace_pool']['var_names']
            if not varnames:
                vars = set()
                for _, var_list in new['namespace_subs'].values():
                    vars.update(lst[0] for lst in var_list)
                varnames[:] = vars

        if validate:
            self._validate_sep_content(new, LearningObj, self.NODE_VALIDATOR)
        return new

    def _get_main(self, name, type, converter):
        lib_addr = '%s/%s' % (type, name)
        node = LibNode(*lib_addr.split('/'))
        with node.open('main') as F:
            new = converter.load(F, F.type)

        # Update fields
        new[u'template_name'] = new[u'name'] = name
        new[u'is_template'] = True
        ctime = node.get_datetime('main')
        ctime = dict((k, getattr(ctime, k)) for k in u'year month day second microsecond'.split())
        new[u'creation_time'] = ctime

        return new, node

    def _validate_sep_content(self, new, validator, sub_validator_f):
        # Validate content separately in order to produce more informative 
        # printing messages
        content = new.pop('content', [])
        new[u'content'] = []
        validator.validate(new, full_errors=True)
        for idx, node in enumerate(content):
            validator = sub_validator_f(node)
            try:
                validator.validate(node, full_errors=True)
            except validator.ValidationError as ex:
                raise type(ex)('at $.content.%s: ' % idx + str(ex))
        new[u'content'] = content

    def get_exam_template(self, name, validate=True, learning_objs={}):
        new, _ = self._get_main(name, 'exam', self.exam_main_import)
        for idx, lobj_name in enumerate(new['content']):
            new['content'][idx] = self.get_learning_obj_template(lobj_name, validate)
        if validate:
            self._validate_sep_content(new, Exam, self.LOBJ_VALIDATOR)
        return new

_lib_template = LibTemplate()
get_learning_obj = _lib_template.get_learning_obj_template
get_exam = _lib_template.get_exam_template

if __name__ == '__main__':
    from pprint import pprint
    obj = get_learning_obj('examples/namespace')
    pprint(obj)


