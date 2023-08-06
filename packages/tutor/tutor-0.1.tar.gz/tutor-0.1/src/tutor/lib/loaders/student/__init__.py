from tutor.config import schemas
from tutor.lib.loaders import from_addr as _from_addr

def from_addr(addr, validate=True, **kwds):
    return _from_addr(schemas.Student, addr, validate, **kwds)
