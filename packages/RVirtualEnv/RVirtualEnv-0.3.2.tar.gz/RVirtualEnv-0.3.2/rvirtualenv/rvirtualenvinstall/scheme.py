import sys
from os import path
import site
from distutils.util import subst_vars

INSTALL_SCHEMES = {
    'custom': {
        'purelib': '$base/lib/python/site-packages',
        'platlib': '$base/lib/python$py_version_short/site-packages',
        'headers': '$base/include/python$py_version_short/$dist_name',
        'scripts': '$base/bin',
        'data'   : '$base/lib/python$py_version_short/site-packages',
        },
    'unix': {
        'purelib': '$base/lib/python$py_version_short/site-packages',
        'platlib': '$base/lib/python$py_version_short/site-packages',
        'headers': '$base/include/python$py_version_short/$dist_name',
        'scripts': '$base/bin',
        'data'   : '$base/lib/python$py_version_short/site-packages',
        },
    'windows': {
        'purelib': '$base/Lib/site-packages',
        'platlib': '$base/Lib/site-packages',
        'headers': '$base/Include/$dist_name',
        'scripts': '$base/Scripts',
        'data'   : '$base/Lib/site-packages',
        },
    'os2': {
        'purelib': '$base/Lib/site-packages',
        'platlib': '$base/Lib/site-packages',
        'headers': '$base/Include/$dist_name',
        'scripts': '$base/Scripts',
        'data'   : '$base/Lib/site-packages',
        },
    'darwin': {
        'purelib': '$base/Library/Python$py_version_short/site-packages',
        'platlib': '$base/Library/Python$py_version_short/site-packages',
        'headers': '$base/Include/$dist_name',
        'scripts': '$base/bin',
        'data'   : '$base/Library/Python$py_version_short/site-packages',
        },
    }

def guess_scheme():
    return 'unix'

def get_scheme(platform, what, vars={}):
    # TODO: maybe use syslinux.get_path in next versions
    replace = {
        'base': sys.prefix,
        'py_version_short': sys.version[:3],
        'dist_name': 'UNKNOWN',
    }
    replace.update(vars)
    line = INSTALL_SCHEMES[platform][what]
    line = path.join(*line.split('/'))
    return subst_vars(line, replace)

def add_to_path(new_paths):
    "add dirs to the beginnig of sys.path"
    __plen = len(sys.path)
    for i in new_paths:
        if i not in sys.path:
            site.addsitedir(i)
    new = sys.path[__plen:]
    del sys.path[__plen:]
    sys.path[0:0] = new

