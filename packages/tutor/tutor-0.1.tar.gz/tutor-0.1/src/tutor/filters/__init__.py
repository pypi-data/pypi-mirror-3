from latex import latex, latex_register, is_filter
DEFAULT = latex
default_filters = dict((k, v) for (k, v) in globals().items() if getattr(v, 'is_filter', False))
