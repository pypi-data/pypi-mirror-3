import json
from tutor.lib import Addr

LOADERS = {}

def from_addr(schema, addr, validate=True, ret_addr=False, **kwds):
    '''
    Generic function that imports objects from library.
    
    Arguments
    ---------
    
    tt : str
        Object type name (e.g.: 'learning_obj', 'exam', etc).
        
    schema : Schema
        Validation schema for object.
        
    addr : str
        Object address in library.
        
    validate : bool
        If True (default), validate result before returning it. 
        
    ret_addr : bool
        If True, return a tuple (json, addr) containing the JSON object plus the 
        Addr() object representing a location in the library.
    '''

    # Format name: e.g.: LearningObj become learning_obj
    last_islower = False
    lower_name = []
    for c in schema.name:
        islower = c.islower()
        if last_islower and (not islower):
            lower_name.append('_')
        last_islower = islower
        lower_name.append(c.lower())
    tt = ''.join(lower_name)

    # Load location on library
    addr_obj = Addr(addr, base=tt)
    if not addr_obj.exists():
        raise IOError('invalid address %s' % addr)

    # Process data
    data_type = addr_obj.get_data_type()
    if data_type == 'json':
        json_obj = json.load(addr_obj.get_data())
    elif data_type == 'cvs':
        json_obj = []
        for line in addr_obj.get_data():
            obj = {}
            args = (a.strip() for a in line.split(','))
            vars = dict(zip(schema.fields, args))
            for k, v in vars.items():
                value = schema[k].from_string(v)
                obj[k] = value
            json_obj.append(obj)
    else:
        try:
            loader = LOADERS[tt][data_type]
        except KeyError:
            raise TypeError('no converters found for %s/%s' % (tt, data_type))
        json_obj = loader(view, validate=False, **kwds)

    # Validate: json_obj can be either a list or a single instance of valid 
    # objects 
    if validate:
        if not isinstance(json_obj, list):
            schema.validate(json_obj)
        else:
            for obj in json_obj:
                schema.validate(obj)

    # Return result
    if ret_addr:
        return json_obj, addr_obj
    else:
        return json_obj

if __name__ == '__main__':
    from tutor.config.schemas import Student
    print from_addr(Student, 'examples/id42')
