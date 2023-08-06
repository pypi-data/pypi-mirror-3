import random as _random

#TODO: choose these numbers more scientifically
_SIZE_MAPPING = {
    'question': 15,
    'exam': 15,
    'revision': 8,
    'person': 8,
    'classroom': 8, }

def rand_id(size, seed=False):
    '''Return a random string that represents a unique id for each object.
    
    Notes
    -----
    
    The default id size for questions and revisions was chosen in order to have
    a very low probability (i.e. < 1e-9) of repetition in some very conservative 
    scenarios.
    '''

    size = _SIZE_MAPPING.get(size, size)

    if seed:
        _random.seed(seed)
    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    return ''.join(_random.choice(chars) for _ in range(size))
