import fs.tempfs
import os
from cStringIO import StringIO
from tutor.util.fs_util import fsitems

class PDFCompileError(Exception):
    pass

def prepare_latex_files(latex_src, media={}):
    '''Prepares and return a temporary directory with the content of ``data`` 
    saved to main.tex. 
    
    The ``media`` parameter can be an fs.FS instance or a mapping from pathnames
    to file objects. These files are copied to the resulting filesystem.
    '''

    root = fs.tempfs.TempFS()
    try:
        items = media.items()
    except AttributeError:
        items = fsitems(media)
    finally:
        for k, v in items:
            with root.open(k, 'w') as F:
                F.write(v.read())

    root.createfile('job_log.log')
    with root.open('main.tex', 'w') as F:
        F.write(latex_src)

    return root

def pdflatex(latex_src, args='', media={}, make_corrections=True):
    r'''Runs ``pdflatex`` in the given LaTeX document and returns it as a file
    object.  
    
    Parameters
    ----------
    latex_src : str
        Source to LaTeX document.
    args : sequence
        Additional arguments to be passed to the ``pdflatex`` command.
    media : dict or fs.FS
        Media files to be used during compilation.
    make_corrections : bool
        Modify latex source in an attempt to correct some bugs from plasTeX.s 
        
    Examples
    --------
    
    >>> pdflatex('\\documentclass{article}\n'
    ...          '\\begin{document}\n'
    ...          'Hello \\LaTeX! I say $1+1=42$.\n'
    ...          '\\end{document}\n')                     # doctest: +ELLIPSIS
    <cStringIO.StringI object at ...>
    '''

    root = prepare_latex_files(latex_src, media)
    syspath = root.getsyspath('')

    # Create pdf
    working_dir = os.getcwd()
    cmd = 'pdflatex -interaction=nonstopmode %s main.tex > job_log.log' % args
    try:
        os.chdir(syspath)
        exit_no = os.system(cmd)
        if exit_no:
            with open('job_log.log') as F:
                logdata = F.read()
            msg = 'pdflatex exited with status (%s)\n\n' % exit_no
            msg += '.' * 80 + '\n'
            msg += logdata
            msg += '\n' + '.' * 80
            raise PDFCompileError(msg)
        with open('main.pdf') as F:
            pdfdata = F.read()
    finally:
        os.chdir(working_dir)

    return StringIO(pdfdata)


def view_pdf(pdf, view='evince'):
    '''Opens a viewer to a pdf file.'''

    root = fs.tempfs.TempFS()
    with root.open('view.pdf', 'w') as F:
        F.write(pdf.read())
    path = root.getsyspath('view.pdf')
    cmd = '%s %s' % (view, path)
    return os.system(cmd)

if __name__ == '__main__':
    import doctest
    doctest.testmod(optionflags=doctest.REPORT_ONLY_FIRST_FAILURE)
