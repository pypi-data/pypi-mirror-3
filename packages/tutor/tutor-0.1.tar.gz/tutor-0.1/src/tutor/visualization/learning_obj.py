from tutor.config import schemas
from tutor.visualization import base
from tutor.visualization.common import Datetime
import string

#===============================================================================
# Pretty printers
#===============================================================================
class Pretty(base.Pretty):
    def __init__(self):
        schema = schemas.LearningObj
        base.Pretty.__init__(self, schema.name, schema.fields)

        self.add_key_transformation('creation_time', Datetime.default.render)
        self.add_key_transformation('date', Datetime.default.render)
        self.add_key_transformation('namespace_pool', base.Pretty(header='\n[ Namespace Pool ]', keys=['type', 'code', 'var_names']).render)
        self.add_array_transformation('content', base.NodeVisualization(base.Pretty, ['name', 'keys']).render)
        self.itemize_array('namespace_subs', itemize=True)
        self.move_to_tail('namespace_subs')
        self.move_to_tail('namespace_pool')
        self.move_to_tail('content')
        self.ommit_keys('namespace_pool', 'content')

#===============================================================================
# Latex/PDF
#===============================================================================
class Tex(base.Tex):
    def __init__(self, document=False):
        base.Tex.__init__(self, 'learningobj_latex', document)
        self._multiple_choice = TexMultipleChoice(document=False)
        self._true_false = TexTrueFalse(document=False)
        self._association = TexAssociation(document=False)
        self._text = TexText(document=False)

    def key_T_creation_time(self, obj):
        return Datetime.default.render(obj)

    def array_T_content(self, obj):
        type = obj['type']
        return getattr(self, '_' + type.replace('-', '_')).render(obj)

# Node types -------------------------------------------------------------------
class TexText(base.Tex):
    def __init__(self, document=False):
        base.Tex.__init__(self, 'text_latex', document)

class TexMultipleChoice(base.Tex):
    def __init__(self, document=False):
        base.Tex.__init__(self, 'multiplechoice_latex', document)

    def T_columns(self, obj):
        if 'columns' not in obj:
            return obj
        columns = obj['columns']

        # Create table_header
        size = (0.9 - columns / 45.) / columns
        col_header = '>{\\raggedright}p{%.3f\\textwidth}' % size
        obj[u'table_header'] = '{%s}' % (col_header * columns)

        # Create table_rows
        letters = list('abcdefghijklmnopqrstuvwxyz')
        elems = obj['items'][:]
        rows = []

        # Create each row
        N, Nc = len(elems), max(columns, 1)
        N_rows = N / Nc + int(bool(N % Nc))

        for _ in range(N_rows):
            cols = []
            for _ in range(Nc):
                try:
                    elem = elems.pop(0)['text'].strip()
                    letter = '%s) ' % letters.pop(0)
                except IndexError:
                    elem = ''
                    letter = ''
                if elem == '$$':
                    elem = '$~$'
                cols.append(letter + elem)
            rows.append(' & '.join(cols))
        obj[u'table_rows'] = rows

        return obj

class TexTrueFalse(base.Tex):
    def __init__(self, document=False):
        base.Tex.__init__(self, 'truefalse_latex', document)

class TexAssociation(base.Tex):
    def __init__(self, document=False):
        base.Tex.__init__(self, 'association_latex', document)

    def T_domain_display(self, obj):
        domain = []
        for item in obj['items']:
            text = item['text_domain']
            if text is not None:
                domain.append(text)
        obj['domain'] = domain
        return obj

    def T_image_display(self, obj):
        image = []
        items = obj['items']
        ordering = obj.get('image_ordering', range(len(items)))
        for idx in ordering:
            item = items[idx]
            item_img = item['text_image']
            image.append(item_img)
        obj['image'] = image
        return obj

    def T_columns_domain(self, obj):
        columns = obj.get('columns_domain', None)
        if columns is None:
            columns = obj.get('columns', None)
            obj['columns_domain'] = columns
        if columns is None:
            return obj

        # Create table_header
        size = (0.9 - columns / 45.) / columns
        col_header = '>{\\raggedright}p{%.3f\\textwidth}' % size
        obj[u'table_header_domain'] = '{%s}' % (col_header * columns)

        # Create table_rows
        letters = iter('I II III IV V VI VII VIII IX X XI XII XIII XIV XV X'.split())
        elems = [ el for el in obj['items'] if el['text_domain'] ]
        rows = []

        # Create each row
        N, Nc = len(elems), max(columns, 1)
        N_rows = N / Nc + int(bool(N % Nc))

        for _ in range(N_rows):
            cols = []
            for _ in range(Nc):
                try:
                    elem = elems.pop(0)['text_domain'].strip()
                    letter = '%s) ' % letters.next()
                except (IndexError, ValueError):
                    elem = ''
                    letter = ''
                if elem == '$$':
                    elem = '$~$'
                if elem:
                    cols.append(letter + elem + ' $\\rightarrow$ \\begin{tabular}{|c|} \\hline ~~~ \\tabularnewline \\hline \\end{tabular}')
                else:
                    cols.append('')
            rows.append(' & '.join(cols))
        obj[u'table_rows_domain'] = rows

        return obj

    def T_columns_image(self, obj):
        columns = obj.get('columns_image', None)
        if columns is None:
            columns = obj.get('columns', None)
            obj['columns_image'] = columns
        if columns is None:
            return obj

        # Create table_header
        size = (0.9 - columns / 45.) / columns
        col_header = '>{\\raggedright}p{%.3f\\textwidth}' % size
        obj[u'table_header_image'] = '{%s}' % (col_header * columns)

        # Create table_rows
        letters = list(string.ascii_lowercase)
        elems = [ el for el in obj['items'] if el['text_image'] ]

        # Re-order elements
        ordering = obj.get('image_ordering', range(len(elems)))
        elems = [ elems[i] for i in ordering ]
        rows = []

        # Create each row
        N, Nc = len(elems), max(columns, 1)
        N_rows = N / Nc + int(bool(N % Nc))

        for _ in range(N_rows):
            cols = []
            for _ in range(Nc):
                try:
                    elem = elems.pop(0)['text_image'].strip()
                    letter = '%s) ' % letters.pop(0)
                except (IndexError, ValueError):
                    elem = ''
                    letter = ''
                if elem == '$$':
                    elem = '$~$'
                if elem:
                    cols.append(letter + elem)
                else:
                    cols.append('')
            rows.append(' & '.join(cols))
        obj[u'table_rows_image'] = rows

        return obj

#===============================================================================
# Responses
#===============================================================================


#===============================================================================
# Tests
#===============================================================================
if __name__ == '__main__':
    from tutor.data.tutor_lib import get_learning_obj
    obj = get_learning_obj('examples/lyx_simple')
    vistex = Tex(False)
    #vispretty = Pretty()
    print vistex.render(obj)
    #vispretty.dump(obj)
