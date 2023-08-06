#-*- coding: utf8 -*-
ascii = [chr(i) for i in range(32, 127)] + list('\0\a\b\t\n\v\f\r')
mapping = {unicode(x): unicode(x) for x in ascii}
keys = ('áa àa âa ãa äa '
         # b
         'çc ĉc '
         # d
         'ée èe êe ẽe ëe '
         # f
         'ǵg ĝg '
         'ĥh ḧh '
         'íi ìi îi ĩi ïi '
         'ĵj '
         'ḱk '
         'ĺl '
         'ḿm '
         'ńn ǹn ñn '
         'óo òo ôo õo öo '
         'ṕp '
         # q
         'ŕr '
         'śs ŝs '
         'ẗt '
         'úu ùu ûu ũu üu '
         'ǘv ǜv ṽv '
         'ẃw ẁw ŵw ẅw '
         'ẍx '
         'ýy ỳy ŷy ỹy ÿy'
         'źz ẑz ').decode('utf8')
keys += keys.upper()
mapping.update({w[:-1]: w[-1:] for w in keys.split()})
mapping = { k.encode('utf32'): v.encode('utf32') for (k, v) in mapping.items() }

def unaccent(st):
    u'''Remove accents from unicode strings
    
    >>> unaccent(u'Fábio Mendes')
    u'Fabio Mendes'
    '''

    st = unicode(st).encode('utf32')
    return ''.join(unaccent_worker(st))

def unaccent_worker(st):
    BOM = ''.encode('utf32')
    for i in range(len(st) / 4 - 1):
        c = BOM + st[i * 4 + 4: (i + 2) * 4]
        try:
            yield mapping[c].decode('utf32')
        except KeyError:
            raise ValueError('unexpected character: %s' % repr(c))

if __name__ == '__main__':
    print unaccent('\nFoo')
    import doctest
    doctest.testmod(optionflags=doctest.REPORT_ONLY_FIRST_FAILURE, verbose=0)
