import os
class Question(object):
    '''
    Question objects
    ----------------
    
    Question objects have a folder-like structure as given bellow. The current 
    implementation uses actual folders, but this is not necessary. Other 
    implementations may, for instance, use a zipped file or a pure JSON object.
    
    <root>
      |- meta.json
      |- src/
      |   |- meta.json
      |   |- template.??? 
      |   \- namespace.???
      |- media/
      |   |- meta.json  
      |   |- any_name.png
      |   |- (...)
      |   \- some other media file.jpeg
      |- extra/
      |   |- meta.json
      |   |- README.txt
      |   |- any file.???
      |   \- foo.bar
      \- data/
          |-123456789/
          |  |- src/
          |  |   \- (...)
          |  |- meta.json
          |  |- template.json
          |  |- child-0.json
          |  |- child-1.json
          |  |- (...)
          |  |- child-N.json
          |  \- children.pdf
          \- 123456700/
              \- (...)
    
    In the previous structure, the "src" folder holds the files that are used to
    generate questions. This usually corresponds to a template file and a script
    used to populate the question's namespace. A few types are supported for 
    the "template.???" file (e.g., LaTeX, LyX, XML, JSON), and this corresponds 
    to the file that end-users should use to create questions. Filenames cannot
    be repeated in this section. Hence, a folder with both a "template.xml" and 
    a "template.tex" files is invalid.
    
    The "media" folder contains media files necessary on compilation of the 
    questions templates. They can be figures, graphs and other content that is 
    not dynamically generated. Many file types are supported (pdf, png, etc), 
    but may require plugins. Files in this folder may be subjected to automatic 
    conversion to other filetypes if this is required by application. (e.g.: an
    EPS file in this folder may be converted to JPEG if this is required to 
    present the Question as a webpage)
    
    The "extra" folder can contain anything. One common use case is to store the 
    source file (e.g.: a GIMP image) before exporting it to the media folder in 
    a supported format. It is recommendable to put a README.txt file explaining 
    what each file in this folder should do.  
          
    The "data" folder contains snapshots of the "src" folder for a given 
    version of the "Question". For all but the most current version, these 
    snapshots are only archival and can be used to revert a given question to a 
    previous state or to restore questions generated with an old version of the
    template. 
    
    A valid "Question" structure must contain almost all files shown above. 
    However, the class method Question.fill_incomplete() can be used fill up the
    blanks if at least "src/template.???" is present. A detailed description of
    the role of each file is given bellow: 
    
    <root>/*/meta.json:
        The meta.json files in each folder contain a valid JSON structure that 
        holds arbitrary meta-information. The root meta.json file can also 
        contain global meta information about the question object.
        
        TODO: document the possible meta information fields (for now, most of 
        these files are empty dictionaries) 
    
    <root>/src/template.???:    
        This file is the main template used generate questions and is usually 
        created by the Question Makers. There are many supported formats, the 
        most common being either LyX or LaTeX sources, but also XML and JSON
        are supported.
        
    <root>/src/namespace.??? (optional)
        A script used to dynamically create the substitution variables used to
        render children questions from the above template. Currently, only 
        Python scripts are available. 
        
    <root>/data/<version_id>/src/*
        Snapshot of the "src" folder at some version of the question script.
        version_id's are integers and the newest versions are represented by 
        larger integers. The current implementation assigns the mean UNIX time
        mtime for each file in /src/, but this behavior is not mandatory.
        
    <root>/data/<version_id>/src/template.json
        The JSON formated structure representing the template.
        
    <root>/data/<version_id>/src/child-*.json
        A list of JSON formated questions generated from the template. Must have
        at least one question object (e.g., at least child-0.json must be 
        present).

    <root>/data/<version_id>/src/children.pdf (optional)
        For convenience, a PDF file displaying all questions in a easy to 
        understand and nicely formatted way. 
            
    '''

    #===========================================================================
    # Exceptions
    #===========================================================================
    class SectionDoesNotExist(Exception):
        pass

    class Invalid(Exception):
        pass

    #===========================================================================
    # Python protocols API
    #===========================================================================
    def __init__(self, path):
        '''
        Open question object in the given 'path'  
        
        @param addr:
        
        Attributes
        ----------
        
        template : JSON-like
            The template object used to generate an arbitrary number of 
            children.
        children : JSON-like    
            List of children objects.
        '''

        self.path = path
        self._opened_files = {}
        self._validate_folder_structure()
        self._create_default_files()
        mean_t = self._mean_time()

        try:
            self._load_section(mean_t)
        except self.SectionDoesNotExist:
            self.reload()

    #===========================================================================
    # API
    #===========================================================================
    @classmethod
    def fill_incomplete(cls, path):
        '''
        Fill incomplete files in a given path from data in src/template.???. 
        Existing files will never be touched.
        '''
        pass

    def reload(self):
        '''
        Create/Recreate children 
        '''
        return

    def append_children(self, size):
        '''
        Create 'size' new children and append them to the 'children' attribute.  
        '''
        return

    def save(self):
        '''
        Saves current state to hard-disk and syncs all opened files.
        '''
        return

    def close(self):
        '''
        Closes all files opened by the resource. 
        '''
        return

    def open(self, path):
        '''
        Opens the file in the given path and return the file object. The method
        obj.close() tries to close all files opened in this way. 
        
        The special path "data/current/" automatically links to the latest 
        snapshot of data. 
        '''
        return

    #===========================================================================
    # Auxiliary methods
    #===========================================================================
    def _validate_folder_structure(self):
        '''
        Raise an Question.Invalid if the folder structure is not compatible 
        with the .qst format defined herein. (Look in the documentation of the 
        Question class for further details.)
        
        Observation: all files ended in '~' are ommited. These files are often
        created by text editors as backup, but are not displayed in most file 
        managers. This files are omitted to avoid the burden on question makers
        to track down and delete these files every time the question templates
        are edited.
        '''

        # Cache useful functions
        pjoin = os.path.join
        pexists = os.path.exists
        if not pexists(pjoin(self.path, 'meta.json')):
            raise self.Invalid("missing file: 'meta.json'")

        #=======================================================================
        # Look if everything is in order in the /src/ folder
        #=======================================================================
        if not pexists(pjoin(self.path, 'src', 'meta.json')):
            raise self.Invalid("missing file: 'src/meta.json'")

        files = os.listdir(pjoin(self.path, 'src'))
        files = [ f for f in files if not f.endswith('~') ]
        del files[files.index('meta.json')]

        # Register the actual path to template.??? and namespace.???
        # --> template
        aux = [ (f.startswith('template.'), f) for f in files ]
        templates = [ f for (is_f, f) in aux if is_f ]
        files = [ f for (is_f, f) in aux if not is_f ]
        if len(templates) == 0:
            raise self.Invalid('template file does not exist')
        elif len(templates) >= 2:
            raise self.Invalid('multiple template files: %s' % (', '.join(templates)))
        else:
            self._src_template_path = pjoin(self.path, 'src', templates[0])

        # --> namespace
        aux = [ (f.startswith('namespace.'), f) for f in files ]
        namespaces = [ f for (is_f, f) in aux if is_f ]
        files = [ f for (is_f, f) in aux if not is_f ]
        if len(namespaces) == 0:
            self._src_namespace_path = None
        elif len(namespaces) >= 2:
            raise self.Invalid('multiple template files: %s' % (', '.join(templates)))
        else:
            self._src_namespace_path = pjoin(self.path, 'src', namespaces[0])

        # Raise an error if there are files remaining
        if files:
            raise self.Invalid('unsupported file(s): %s' % (', '.join(files)))

        #=======================================================================
        # Look if everything is in order in the /media/ folder
        #=======================================================================

        #=======================================================================
        # Look if everything is in order in the /extra/ folder
        #=======================================================================

        #=======================================================================
        # Look if everything is in order in the /data/ folder
        #=======================================================================

    def _create_default_files(self):
        '''
        Create necessary files that are not present.
        '''
        return

    def _mean_time(self):
        '''
        Return the mean UNIX-mtime of all files in the 'src' sub-folder.         
        '''
        templ_t = os.stat(self._src_template_path).st_mtime
        if self._src_namespace_path is not None:
            names_t = os.stat(self._src_namespace_path).st_mtime
        else:
            names_t = templ_t

        return int((templ_t + names_t) / 2)

    def _load_section(self, section_id):
        '''
        Load all relevant files in the section identified by a given id.        
        '''
        return

    #===========================================================================
    # Attributes representing files
    #===========================================================================



    # We exploit the metaclass mechanism to automatically create property 
    # attributes that serve as assessors for files in the folder hierarchy  
#    class _file_some_obj(object):
#        class __metaclass__


if __name__ == '__main__':
    example_path = '../../../../../lib/lib/examples/pure lyx file.qst'
    Question.fill_incomplete(example_path)
    Question(example_path)
