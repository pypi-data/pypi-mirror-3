#-*- coding: utf8 -*-
'''
Manipulates question files/directories and provide a JSON-like translation to 
these objects.

QuestionPool files
--------------

QuestionT objects are most likely stored in ``.qst`` files or a ``.qst`` folder 
structure in the user's filesystem. This module exports functions that provide 
an automatic translation of these files into JSON structures that represents 
the corresponding history.

QuestionT storage objects are recognized by being either files or folders ending 
with a .qst extension. QuestionT files are simply zipped .qst folders (with the
.qst extension, instead of .zip or .tar.gz).

The file structure in the .qst folders resembles the JSON hierarchy for QuestionT
objects and is described and defined bellow:

  src: 
     Template source files. **Must** contain a "main.*" file that represents the 
     question template in a human friendly format. For now, only .tex and .lyx
     files are supported. Optionally, it may contain a script or database file 
     that is used to generate random variables to fill in values in the 
     template. For now, only Python scripts are supported. This script must be 
     named as "namespace.py".  
  
  src/media: 
     Static media files. This feature is not supported yet.

  src/aux:
      Contain any user-generated file. The tutor system will not touch the 
      files in this folder. It is useful, for instance, to store the master 
      files for the media content (e.g, a GIMP .xcf file) that will later be 
      exported in a latex friendly format such as .png or .pdf.
      
  history:
      Contains a list of revisions of the question object. Each revision is 
      stored in a sub-folder that is named after a unique randomized id. Inside
      each folder, there is a copy of the "history" and "media" sub-folders 
      and a "root.json" file that contains configuration parameters. 
'''
from __future__ import absolute_import, print_function, unicode_literals, division
from future_builtins import * #@UnusedWildImport
if __name__ == '__main__':
    __package__ = b'tutor.types' #@ReservedAssignment
    import tutor.types #@UnusedImport

from datetime import datetime
import fs.osfs
import tutor.version
from ..latex.commands import lyxtotex
from ..history import History
from ..util.rand_id import rand_id
from ..util.relational import ManyToOne
from ..paths import SYSTEM_EXAMPLES_DIR
from .subquestions import SubQuestion, Scoring
from .namespace import CodeNS
from .src_folder import SrcFolder
from .pool_view import PoolView
from .schema import (SchemaObj, sch_instance, array_of, Opt,
                     Str, Datetime, Array, Folder, Dict, Number)

examples = fs.osfs.OSFS(SYSTEM_EXAMPLES_DIR)
#===============================================================================
# QuestionPool Type
#===============================================================================
class QuestionPool(SchemaObj):
    '''Represents groups of Question objects organized in different sequential 
    revisions. 
    
    Actual questions can be retrieved using a index notation from a QuestionPool
    object using a (revision_no, revision_key) tuple:
    
    >>> qpool = QuestionPool('foo', title='My Question')
    >>> qpool.commit(10)
    >>> qpool[-1, 0] # first object of the last revision # doctest: +ELLIPSIS
    <...Question object at 0x...>
    '''
    class schema(sch_instance):
        id = Str() #@ReservedAssignment
        name = Str()
        title = Str()
        author = Str()
        version = Str()
        ctime = Datetime()
        value = Number(1.0)
        comment = Opt(Str())
        history = Array()
        src = Folder()

    def __init__(self, name='', title=' ', author=' ',
                       comment='', ctime=None, id=None, src=None, #@ReservedAssignment
                       main_t='tex', main_data=None,
                       namespace_t='py', namespace_data=None):
        '''Creates a new empty question. 
    
        Parameters
        ----------
        name : str
            Name for the new question.
        main : str
            A string describing the prefered type for the src/main.* file. Accepted
            values are: 'tex', 'lyx', and 'xml'.
        question_id : str
            The question id can be set manually, if required.
            
        Examples
        --------
        
        >>> qst = QuestionPool('foo.qst')
        >>> qst.name, qst.author  
        (u'foo.qst', u'')
        '''
        super(QuestionPool, self).__init__()

        self.id = id or rand_id('question')
        self.name = unicode(name)
        self.title = unicode(title)
        self.author = unicode(author)
        self.ctime = ctime if ctime is not None else datetime.now()
        self.history = History()
        self.comment = unicode(comment)
        self.version = tutor.version.VERSION

        # Populate the /src dir
        if src is not None:
            self.src = src
        else:
            self.src = SrcFolder()
            base = examples.opendir('questions/base-src')
            with self.src.open_main(type=main_t) as F_dest:
                if main_data is None:
                    with base.open('main.lyx') as F:
                        if main_t == 'tex':
                            F = lyxtotex(F)
                            main_data = F.read().decode('utf8')
                    main_data = main_data.replace('QuestionTitle', title)
                    main_data = main_data.replace('QuestionAuthor', author)
                    main_data = main_data.replace('QuestionDate', str(datetime.now()))
                    del F

                F_dest.write(main_data.encode('utf8'))
            with self.src.open_namespace(type=namespace_t) as F_dest:
                if namespace_data is None:
                    with base.open('namespace.py') as F:
                        namespace_data = F.read().decode('utf8')
                F_dest.write(namespace_data.encode('utf8'))

        # Commit question
        self.commit(0, final=False)

    def commit(self, size=50, final=True, ammend=False):
        '''Saves the changes in the src files into the question structure and 
        render ``size`` history from the template. 
        
        Examples
        --------
        
        Creates and dump 42 versions of the question from its template.
        
        >>> qst = QuestionPool('foo.qst')
        
        There is one item in the last revision corresponding to the template
        
        >>> qst.history.last # doctest: +ELLIPSIS
        <Revision "..." (2 items)>
        
        After committing 42 new questions, the last revision will have 44 items
        (42 questions + template + meta):
        
        >>> qst.commit(42)
        >>> qst.history.last # doctest: +ELLIPSIS
        <Revision "..." (44 items)>
        
        Notes
        -----
        The default value of 50 for ``size`` was chosen so there is an approximate 
        chance of 85% for a student taking a test in a classroom has none of its
        typical 9 neighbors (front, back, sides and diagonals) taking the same
        version of the question.
        '''
        from .qst_import.latex_src import load_main_tex, load_main_lyx

        # Propagate changes in tip to question structure 
        # (read src/main and src/namespace)
        if self.src.main_t == 'tex':
            with self.src.open_main() as F:
                template = load_main_tex(F)
        elif self.src.main_t == 'lyx':
            with self.src.open_main() as F:
                template = load_main_lyx(F)
        else:
            raise ValueError("main can a 'tex' or 'lyx' file, got: %s" % self.src.main_path)

        # Saves data from loader in question
        for k, v in template['root'].items():
            setattr(self, k, v)
        del template['root']

        # Read namespace
        #TODO: make this a nice object
        with self.src.open_namespace() as F:
            template[u'namespace'] = {
                u'type': u'tutor-question:namespace',
                u'content': u'python-script',
                u'data': F.read() }

        # Creates a new revision
        if ammend:
            raise NotImplementedError
        else:
            meta = self.history[-1].setdefault('meta', {}) if self.history else {}
            if self.history and (not meta.get('final', True)):
                self.history.pop()
            revision = self.history.new_revision()
            revision['template'] = template
            revision['meta'] = {'final': final}

        # Apply namespaces to templates and create new history
        namespace = CodeNS(template['namespace']['data'])
        for idx in range(size):
            for _ in range(20):
                renderer = namespace.new_renderer()
                body = []
                for subq_t in template['body']:
                    subq = subq_t.copy(keep_parent=False)
                    try:
                        subq.format(renderer)
                    except ValueError:
                        break
                    subq.adapt(inplace=True, force=True)
                    body.append(subq)
                else:
                    revision[str(idx)] = body
                    break
            else:
                text = '\n    '.join(item.text for item in subq.items)
                raise RuntimeError('maximum number of attempts trying to create subquestion:\n    %s' % text)

    def template(self, revision= -1):
        '''Return the template for the given revision'''

        return self.history[revision]['template']

    def preamble(self, revision= -1):
        '''Return the preamble for the given revision'''

        return self.history.last['template']['preamble']

    def __getitem__(self, key):
        rev, key = key
        return Question(self, rev, key)

class Preamble(SchemaObj):
    class schema(sch_instance):
        documentclass = Str()
        options = Dict()
        class packages(array_of):
            name = Str()
            options = Dict()

class Question(PoolView):
    '''View data from a specific question in a QuestionPool object.
    
    Parameters
    ----------
    
    pool : QuestionPool
        Parent object that contains the question.
    rev_no : str or int
        Revision number or id
    rev_key : str
        Revision key
    '''
    children = SubQuestion.parent.symmetrical
    parent = ManyToOne()

    def __init__(self, pool, rev_no, rev_key):
        super(Question, self).__init__(pool, rev_no, rev_key)
        revision = pool.history[self._revision_no]
        self.body = revision[self._revision_key]
        for obj in self.body:
            obj.parent = self

    @property
    def src(self):
        return self._pool.src

    @property
    def preamble(self):
        return self._pool.history[self._revision_no]['template']['preamble']

    def exam_index(self):
        '''Returns the index of question in the parent exam'''

        return self.parent.body.index(self)

    @property
    def scoring(self):
        '''List of scoring sub-questions'''

        return [ x for x in self if isinstance(x, Scoring)]

    def subquestion(self, idx, scoring=False):
        '''Return the sub-question in the given index. If scoring is True, 
        counts only scoring sub-questions'''

        if scoring:
            body = (x for x in self.body if isinstance(x, Scoring))
            for i, x in enumerate(body):
                if i == idx:
                    return x
            else:
                raise ValueError('%s not in list' % self)
        else:
            return self.body[idx]

if __name__ == '__main__':
    q = QuestionPool('foo', author='Fábio Mendes', title='Foo')
    q.commit(20)
    print(q.src.open('main.tex').read())
    print(q[-1, 2][0])

    import doctest
    doctest.testmod()
