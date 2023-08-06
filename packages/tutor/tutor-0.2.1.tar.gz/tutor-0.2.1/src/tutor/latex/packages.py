import tutor.plastex

__all__ = ['Package', 'PackageGroup']

class Package(object):
    r'''Class that represents a LaTeX package.
    
    Construct a ``Package`` instance from its name and the option string or
    from an options dictionary.
    
    Examples
    --------
    
    >>> p = Package('inputenc', 'latin9'); p.render()
    u'\\usepackage[latin9]{inputenc}'

    >>> p = Package('inputenc', latin9=True); p.render()
    u'\\usepackage[latin9]{inputenc}'
    '''
    def __new__(cls, name, options_string=None, **options):
        if options_string is None:
            obj = super(Package, cls).__new__(cls)
            obj.name = unicode(name)
            obj.options = options
            return obj
        else:
            obj = Package.from_latex(u'\\usepackage[%s]{%s}' % (options_string, name))
            obj.options.update(options)
            return obj

    @classmethod
    def from_latex(cls, cmd):
        r'''Construct a ``Package`` instance from the corresponding latex 
        command.
        
        Examples
        --------
        
        >>> p = Package.from_latex('\usepackage[latin9]{inputenc}')
        >>> p.render()
        u'\\usepackage[latin9]{inputenc}'
        '''
        parsed = tutor.plastex.parse(cmd.strip())[0]
        if parsed.tagName != 'usepackage':
            raise ValueError('not a \\usepackage command: %s' % cmd)
        else:
            name = parsed.getAttribute('names')[0]
            options = parsed.getAttribute('options')
            return Package(name, **options)

    @property
    def option_str(self):
        if not self.options:
            return u''
        else:
            data = ['[']
            for k, v in self.options.items():
                if v == True:
                    data.append(k)
                else:
                    data.append('%s=%s' % (k, v))
            data.append(']')
            return u''.join(data)

    def render(self):
        '''Renders the corresponding \\usepackage LaTeX command to a string.'''

        return u'\\usepackage%s{%s}' % (self.option_str, self.name)

    def __str__(self):
        return "<Package '%s'>" % self.name

class PackageGroup(object):
    '''Class that represents a group of unique LaTeX packages.
    
    Examples
    --------
    
    >>> packages = [Package('amsmath'), Package('inputenc', 'utf8'), Package('amsmath')]
    >>> pg = PackageGroup(packages)
    >>> print(pg.render())
    \usepackage{amsmath}
    \usepackage[utf8]{inputenc}
    '''

    def __init__(self, packages=[]):
        self._plist = []
        self._packages = {}
        for p in packages:
            self.append(p, True)

    def append(self, package, overwrite=False):
        '''Adds a package to the group.'''

        # Compares with existing package
        if not overwrite:
            try:
                p_exists = self._packages[package.name]
                if p_exists != package:
                    raise ValueError('conflicts with package: %s' % p_exists.render())
            except KeyError:
                pass

        if package.name not in self._packages:
            self._plist.append(package.name)

        self._packages[package.name] = package

    def render(self):
        '''Renders the corresponding LaTeX commands to a string.'''

        return '\n'.join(p.render() for p in self.packages)

    @property
    def packages(self):
        P = self._packages
        return [ P[name] for name in self._plist ]

    def __str__(self):
        return "<PackageGroup, '%s'>" % (', '.join(p.name for p in self.packages))


if __name__ == '__main__':
    import doctest
    doctest.testmod(optionflags=doctest.REPORT_ONLY_FIRST_FAILURE)
