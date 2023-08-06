import pyson, bz2
# deprecaded, it will stay here until all old objects are converted to their
# newer versions

def dump(obj, F, header='<generic>', version='<generic>'):
    data = pyson.dumps(obj)
    data = bz2.compress(data)

    # Write to file
    F.write(header)
    F.write(version)
    F.write('\n%s\n' % len(data))
    F.write(data)

def load(F, header='<generic>', version='<generic>'):
    header_data = F.readline()
    size = F.readline()
    data = F.read()

    # Type and version check
    if not header_data.startswith(header):
        raise ValueError("not a valid question")
    obj_version = header_data[len(header):-1]
    if obj_version != version:
        raise ValueError("unsupported version: %s" % obj_version)

    # Consistency check on data
    size = int(size.strip())
    if len(data) != size:
        raise TypeError('corrupted file!')

    # Uncompress data
    data = bz2.decompress(data)
    return pyson.loads(data)
