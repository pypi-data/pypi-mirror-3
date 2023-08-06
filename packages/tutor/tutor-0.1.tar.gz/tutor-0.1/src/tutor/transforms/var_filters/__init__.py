from latex import latex, latex_register, is_filter
DEFAULT = latex
DEFAULT_FILTERS = dict((k, v) for (k, v) in globals().items() if getattr(v, 'is_filter', False))
