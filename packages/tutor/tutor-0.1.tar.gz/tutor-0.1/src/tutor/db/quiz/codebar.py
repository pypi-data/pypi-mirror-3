class Codebar(object):
    PSTRICKS_PACKAGE_IMPORT = '\\usepackage{pstricks}'
    DEFAULT_ALPHABET = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    
    def __init__(self, alphabet=DEFAULT_ALPHABET):
        self._data = []
        self.alphabet = alphabet
    
    def add_code(self, nbits, number, base=2):
        if isinstance(number, basestring):
            if len(number) != 1:
                raise ValueError("'number' must be a single character string, got '%s'" % number)
            number = self.alphabet.find(number)
        
        self._data.append((int(nbits), int(number)))
    
    def print_code(self, base=2):
        pass

    def print_pstricks(self, 
                       base=2, 
                       full_code=False, 
                       codification='code128',
                       scale=None,
                       options='showtext',
                       prepend=None,
                       separator='!'):
        pass
    
    @staticmethod
    def print_pstrics_header():
        return Codebar.PSTRICKS_PACKAGE_IMPORT
    
if __name__ == '__main__':
    pass