# Future -----------------------------------------------------------------------
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
if __name__ == '__main__':
    __package__ = b'tutor.visualization' #@ReservedAssignment
    import tutor.visualization #@UnusedImport
#-------------------------------------------------------------------------------

import abc

class Renderer(object):
    __metaclass__ = abc.ABCMeta

    @classmethod
    def __subclasshook(cls, other):
        if hasattr(other, 'render') and hasattr(other, 'renderers'):
            return True
        else:
            return NotImplemented

    def render(self, method, **kwds):
        '''Automatic dispatch of render functions according with the rendering 
        method:
            obj.render('foo', **kwds) <==> obj.render_foo(**kwds)
        '''
        try:
            renderer = getattr(self, 'render_' + method)
        except AttributeError:
            raise ValueError('method not supported: %s' % method)
        return renderer(**kwds)

    def renderers(self):
        '''Return a tuple with all supported rendering methods'''

        return tuple(m for m in dir(self) if m.startswith('render_'))

if __name__ == '__main__':
    import doctest
    doctest.testmod(optionflags=doctest.REPORT_ONLY_FIRST_FAILURE)
