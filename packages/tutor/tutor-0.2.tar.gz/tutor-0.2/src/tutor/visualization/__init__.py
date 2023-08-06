'''
The visualization capabilities of PyTutor are concentrated in two functions:
the ``render(obj, method)`` and ``render_template(tmpl, method, ns)``. The 
first function renders arbitrary objects within PyTutor system and the second 
renders a template string using the variables in the given namespace. 

=========================
The ``render()`` function
=========================

The render function ...

**Parameters**
  obj : any supported object
      Object that should be rendererd
  method : str
      Name of the sub-renderer method that should do the actual rendering. 
      See the section `Sub-rendenderers` for more information.
  
Each sub-renderer and even each type can define additional optional keyword
arguments that controls how rendering is performed. The user must consult the 
documentation on each sub-renderer method for extra information.   
      

Sub-renderers
=============

LaTeX - ``latex``
-----------------

asdads

pdfLaTeX - ``pdflatex``
-----------------------

asas

Pretty Print - ``pprint``
-------------------------

Not implemented yet.

==================================
The ``render_template()`` function
==================================

The render_template() function ...

Sub-renderers
=============

LaTeX - ``latex``
-----------------

sdas

XHTML - ``xhtml``
-----------------

Not implemented yet.

Text - ``text``
---------------

Not implemented yet.
 
'''
from __future__ import absolute_import, print_function, unicode_literals, division
if __name__ == '__main__':
    __package__ = b'tutor.visualization' #@ReservedAssignment
    import tutor.visualization #@UnresolvedImport
#-------------------------------------------------------------------------------

from .types import Renderer
from .render_base import render, latex, pprint, xhtml, pdflatex
from .render_exam import *
from .render_subquestions import *
from .render_question import *
from .template import render_template
