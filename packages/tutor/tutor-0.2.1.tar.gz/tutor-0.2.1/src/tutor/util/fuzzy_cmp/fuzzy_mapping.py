import sys
from cStringIO import StringIO
import numpy as np

__all__ = [ 'associate_keys' ]

def associate_keys(
        wrong_keys, right_keys,
        distance=None, args=(), kwds={},
        bijective=False, skip_equal=True, max_dist=None,
        disp=True, full_output=False):
    '''
    Given a list of 'wrong_keys' which were corrupted by replacing or adding and 
    removing a few characters, tries to infer the correct value from the list of
    'right_keys'.
    
    Arguments
    ---------
    wrong_keys : iterable
        List of corrupted keys.
    right_keys : iterable
        List of the accepted value for the keys.
    distance : function(key1, key2)
        Function that computs the distance/divergence between two keys. By 
        default, it uses the Levenshstein distance between two string keys.
        It can be changed to use different notions of divergence between strings
        or to support different objects.
    skip_equal : bool
        If True, it automatically associates identical keys with each other.
        This option does not affect the results if distance(x, x) == 0, but can
        make the algorithm run significantly faster if there are a lot of 
        identical (wrong_key, right_key) pairs.
    max_dist : float
        If the optimal pairwise distance is greater than max_dist, the mapping 
        will not be added to the output. Instead, it will map the 'wkey' to 
        None.  
    args, kwds : tuple and dictionary
        Optional positional an keyword arguments to pass to the distance 
        function.
    bijective : bool
        If True, each wrong_key can be associated to a single right_key.
    disp : bool
        If False, does not display any warning messages. The user may prefer to 
        collect the warning messages from the function output (see full_output
        bellow).
    full_output : bool
        If True, outputs additional information about warning messages and 
        convergence.
        
    Output
    ------
    
    Returns a dictionary of {wrong_key: right_key} associations. If full_output is
    enabled, returns a tuple with this dictionary and a dictionary with information
    on convergence and warnings.
    
    Algorithm
    ---------
    
    The classification is done trying to minimize the sum of distances
    between all pairs of keys. If the association is not bijective, it 
    simply maps each wrong key to the 'closest' right key.
    '''

    # Error checks
    if not right_keys: raise ValueError("'right_keys' is empty.")
    if not wrong_keys: raise ValueError("'wrong_keys' is empty.")

    # Default distance function
    if distance is None:
        import Levenshtein
        distance = Levenshtein.distance

    # Wraps distance function to raise an uniform ValueError in case of failure
    def wrapped_distance(x, y):
        try:
            out = distance(x, y, *args, **kwds)
        except Exception as ex:
            new_ex = ValueError('error caught in the distance function: %s' % ex)
            new_ex.exception = ex
            new_ex.func_args = (x, y)
            raise new_ex
        return out

    wkeys = set(wrong_keys)
    rkeys = set(right_keys)

    # Should we skip identical keys?
    if skip_equal:
        repeated = rkeys.intersection(wkeys)
        wkeys.difference_update(repeated)
        if bijective:
            rkeys.difference_update(repeated)
        repeated = dict((x, x) for x in repeated)

    # Select worker and execute it according to the chosen algorithm
    # Each worker is implemented to always display messages and to always
    # enable full output. 
    if bijective:
        worker = worker_bijective
    else:
        worker = worker_standard

    if disp:
        out_map, warns = worker(wkeys, rkeys, wrapped_distance)
    else:
        # Capture messages
        std_old = sys.stdout
        try:
            sys.stdout = StringIO()
            out_map, warns = worker(wkeys, rkeys, wrapped_distance)
        finally:
            sys.stdout = std_old

    # Check if maximum distance was obtained
    if max_dist is not None:
        for key, dist in warns['distances'].items():
            if dist > max_dist:
                out_map[key] = None

    # Processes output
    if skip_equal:
        out_map.update(repeated)
    if full_output:
        return out_map, warns
    else:
        return out_map

def worker_bijective(wkeys, rkeys, D):
    '''
    Worker function for the bijective algorithm
    '''

    def sum_sqrs(idxs):
        getter = dists.__getitem__
        return sum(getter(pt) for pt in enumerate(idxs))

    # Initialize the distance matrix
    wkeys, rkeys = list(wkeys), list(rkeys)
    dists = np.zeros((len(wkeys), len(rkeys)), dtype=np.float)
    M, N = dists.shape
    for i, wkey in enumerate(wkeys):
        for j, rkey in enumerate(rkeys):
            dists[i, j] = D(wkey, rkey)
    fdists = dists.flatten()

    # Tries to optimize the list of indexes with smaller sum of distances

    #TODO: this algorithm does not necessarily leads to the optimum solution.
    # It is however reasonably fast and it seems to be that the brute force
    # approach would be an O(exp) operation.
    out_map = {}
    dist_map = {}
    widxs = set(range(len(wkeys)))
    ridxs = set(range(len(rkeys)))
    for flat_idx in fdists.argsort():
        i, j = flat_idx / N, flat_idx % N
        if (i in widxs) and (j in ridxs):
            widxs.discard(i)
            ridxs.discard(j)
            out_map[wkeys[i]] = rkeys[j]
            dist_map[wkeys[i]] = dists[i, j]
        else:
            if not widxs:
                break
#    out_mapping = dict((wkeys[i], rkeys[j]) for (i, j) in enumerate(out_idxs))
    return out_map, { 'distances': dist_map }

def worker_standard(wkeys, rkeys, D):
    '''
    Worker function for the non-bijective algorithm
    '''
    out_mapping = {}
    dist_map = {}
    for key in wkeys:
        dists = [ (D(key, x), x) for x in rkeys ]
        dists.sort()
        dmin, best = dists[0]
        dist_map[key] = dmin
        out_mapping[key] = best
        for d, x in dists[1:]:
            if d == dmin:
                print 'repeated'
            else:
                break

    return out_mapping, { 'distances': dist_map }


if __name__ == '__main__':
    rkeys = ['foo', 'bar', 'eggs', 'spam', 'ham', 'none']
    wkeys = ['fo0', 'bar', 'egg', 'span', 'blah']
    print associate_keys(wkeys, rkeys, bijective=True)
    print associate_keys(wkeys, rkeys, bijective=False)
