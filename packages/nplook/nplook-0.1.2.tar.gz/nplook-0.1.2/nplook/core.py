
from __future__ import print_function
import sys
import numpy as np

def represent(obj):
    if isinstance(obj, np.ndarray):
        if obj.shape == ():
            return '{0} [{1}]'.format(repr(obj[()]), obj.dtype)
        else:
            return "ndarray {0} [{1}]".format(obj.shape, obj.dtype)
    elif isinstance(obj, str):
        return "string ({0})".format(len(obj))
    else:
        lines = repr(obj).split("\n")
        if len(lines) > 5:
            lines = lines[:5] + ["..."]
        return "\n".join(lines)

def summarize(filename):
    s = ""
    try:
        data = np.load(filename)
    except IOError:
        data = None

    status = ''
    if data is None:
        return None#status = 'FILE NOT FOUND!'

    s += "-> {0} {1}\n".format(filename, status)
    
    if isinstance(data, np.lib.npyio.NpzFile):
        N = max(map(lambda x: len(x), data.keys()))
        indent = 3
        for k in data.keys():
            x = represent(data[k])
            x = x.replace('\n', '\n'+' '*(N+2 + indent))
            s += " "*indent + "{0} : {1}\n".format(k.rjust(N), x)
    else:
        indent = 3
        x = represent(data)
        x = x.replace('\n', '\n'+' '*(indent))
        s += " "*indent + x

    # Remove the last newline
    if s[-1] == '\n':
        s = s[:-1]
    return s

