#-*- coding: utf8 -*-
from tutor.visualization import base, learning_obj
from tutor.visualization.common import Datetime
import string

#===============================================================================
# Pretty print
#===============================================================================
class Pretty(base.Pretty):
    def __init__(self):
        super(Pretty, self).__init__()
        self.add_key_transformation('creation_time', Datetime().render)

#===============================================================================
# Latex/PDF
#===============================================================================
class Tex(base.Tex):
    def __init__(self, document=False):
        base.Tex.__init__(self, 'exam_latex', document)
        self._lobj = learning_obj.Tex(document=False)

    def array_T_content(self, obj):
        return self._lobj.render(obj)

    def T_barcode_scale(self, obj):
        obj.setdefault('barcode_scale', 1)
        return obj

#===============================================================================
# Responses
#===============================================================================
class Response(base.Visualization):
    def __init__(self):
        super(Response, self).__init__()
        self._lobj_vis = None

    def render(self, obj):
        out = ['\n[ Gabarito: %s ]\n' % obj['title'],
               '  Id: "%s"' % obj['name']]

        for idx, lobj in enumerate(obj['content']):
            lines = []
            for item in lobj['content']:
                tt = item['type']
                method = getattr(self, 'resp_%s' % (tt.replace('-', '_')))
                lines.append(method(item))
            lines = filter(None, lines)

            # Format lines and prepend indexing
            q_no = str(idx + 1).rjust(2)
            if len(lines) == 1:
                data = '\n  %s) %s' % (q_no, lines[0])
            else:
                letters = iter(string.ascii_lowercase)
                lines = [ '%s.%s) %s' % (q_no, c, l) for (c, l) in zip(letters, lines) ]
                data = '\n' + '\n'.join(lines)

            out.append(data)
        return ''.join(out)

    def resp_multiple_choice(self, lobj):
        items = lobj['items']
        values = {}
        for letter, item in zip(string.ascii_lowercase, items):
            value = item.get('value', None)
            if value:
                values[letter] = value

        # Extract correct value
        values = values.items()
        values.sort(key=lambda (k, v): v)
        right, max_value = values.pop()
        right *= 2
        if values:
            while values[-1][1] == max_value:
                other_right, _ = values.pop()
                other_right *= 2
                right = '%s, %s' % (right, other_right)
        right = right.upper()

        if not values:
            return right
        else:
            max_value = float(max_value)
            values.reverse()
            values = [ (k, v / max_value) for (k, v) in values ]
            values.sort(key=lambda (k, v): k)
            values = [ '\n      %s: %0.2f%%' % item for item in values ]
            return '%s%s' % (right, ''.join(values))

if __name__ == '__main__':
    from tutor.data.tutor_lib import get_exam
    from tutor.visualization.base import Pdf
    from tutor.transforms import creation

    #obj = get_exam('examples/simple_exam')
    obj = get_exam('cálculo 3/módulo 5/lista')
    obj = creation.new_exam(obj)

    vistex = Tex(True)
    vispdf = Pdf(vistex)
    vispretty = Pretty()
    print vistex.render(obj)
    vispdf.dump(obj, '~/foo.pdf')
#    vispretty.dump(obj)

