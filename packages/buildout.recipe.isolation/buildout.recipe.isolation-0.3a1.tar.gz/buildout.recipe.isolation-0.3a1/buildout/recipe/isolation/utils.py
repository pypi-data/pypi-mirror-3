# -*- coding: utf-8 -*-
import pkg_resources


def filter_working_set(incl_ws, excl_ws):
    ws = pkg_resources.WorkingSet([])
    excluded_dists = excl_ws.by_key.keys()

    for name, dist in incl_ws.by_key.iteritems():
        if name not in excluded_dists:
            ws.add(dist)
    return ws

def remove_setuptools(ws):
    """Remove setuptools/distribute distribution from the working set (ws)."""
    # Unfortunately, the pkg_resources.WorkingSet doesn't have a
    # method to remove distributions from the set.
    r = pkg_resources.Requirement.parse('setuptools')
    dist = ws.find(r)
    if dist:
        for k, v in ws.entry_keys.items():
            if dist.key in v:
                # Remove from the entry_keys dictionary.
                del ws.entry_keys[k]
                # Remove from previously from the entries list.
                ws.entries.remove(k)
        # Finally, remove the distribution from the by_keys dictionary.
        del ws.by_key[dist.key]
    return ws

def write_path_file(working_set, filename='isolated.pth'):
    """Write out a .pth file from the given working set.
    The filename argument can be a filename, which means the file will
    be written to the current working directory, or it can be a full path
    to the file."""
    pth = open(filename, 'w')  # BBB Python <= 2.4
    for dist in working_set.by_key.values():
        pth.write(dist.location + '\n')
    pth.close()

def as_bool(value):
    """Parse a value for it's boolean equivalent."""
    if value is None:
        value = False
    elif isinstance(value, bool) or isinstance(value, int):
        pass
    elif isinstance(value, str):
        value = value.lower()
        if value == 'true':
            value = True
        else:
            value = False
    else:
        raise TypeError("Could not determine the boolean value of "
            "%s." % value)
    return value

def as_list(value):
    """Parse a value for it's list equivalent."""
    if value is None:
        value = []
    elif isinstance(value, list) or isinstance(value, tuple):
        pass
    elif isinstance(value, str):
        value = [ v for v in value.split('\n') if v ]
    else:
        raise TypeError("Could not parse the list value of %s." % value)
    return value

def as_string(value):
    """Parse a value for it's equivalent string reprsentation."""
    if value is None:
        value = ''
    elif isinstance(value, str) or isinstance(value, int):
        value = str(value)
    elif isinstance(value, list) or isinstance(value, tuple):
        numb = []
        if len(value) > 1:
            numb = ['']
        value = '\n'.join(numb + value)
    elif isinstance(value, bool):
        if value:
            value = 'true'
        else:
            value = 'false'
    else:
        raise TypeError("Could not transform the value %s into a string."
                        % value)
    return value
