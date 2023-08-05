# pylint: disable-msg=W0622
"""cubicweb-jpl application packaging information

Copyright (c) 2003-2010 LOGILAB S.A. (Paris, FRANCE).
http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

modname = 'jpl'
distname = "cubicweb-jpl"

numversion = (0, 34, 0)
version = '.'.join(str(num) for num in numversion)

license = 'LCL'

author = "Logilab"
author_email = "contact@logilab.fr"
web = 'http://intranet.logilab.fr/jpl/project/cubicweb-jpl'

description = "forge component for logilab applications"

__depends__ = {'cubicweb': '>= 3.8.0',
               'cubicweb-forge': '>= 0.1.0',
               'cubicweb-vcsfile': '>= 1.5.0',
               'cubicweb-apycot': '>= 2.0.0'
               }

# packaging ###

from os import listdir as _listdir
from os.path import join, isdir, exists, dirname
from glob import glob

THIS_CUBE_DIR = join('share', 'cubicweb', 'cubes', modname)

def listdir(dirpath):
    return [join(dirpath, fname) for fname in _listdir(dirpath)
            if fname[0] != '.' and not fname.endswith('.pyc')
            and not fname.endswith('~')
            and not isdir(join(dirpath, fname))]

data_files = [
    # common files
    [THIS_CUBE_DIR, [fname for fname in glob('*.py') if fname != 'setup.py']],
    ]
# check for possible extended cube layout
for dirname in ('entities', 'views', 'sobjects', 'hooks', 'schema', 'data', 'i18n', 'migration'):
    if isdir(dirname):
        data_files.append([join(THIS_CUBE_DIR, dirname), listdir(dirname)])
# Note: here, you'll need to add subdirectories if you want
# them to be included in the debian package

