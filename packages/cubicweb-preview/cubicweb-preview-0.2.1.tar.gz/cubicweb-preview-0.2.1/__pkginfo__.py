# pylint: disable-msg=W0622
"""cubicweb-preview application packaging information"""

modname = 'preview'
distname = 'cubicweb-preview'

numversion = (0, 2, 1)
version = '.'.join(str(num) for num in numversion)

license = 'LCL'
copyright = '''Copyright (c) 2010 SECOND WEB S.A.S. (Paris, FRANCE).
http://www.secondweb.fr -- mailto:contact@secondweb.fr'''

author = 'SECOND WEB S.A.S. (Paris, FRANCE)'
author_email = 'contact@secondweb.fr'

short_desc = 'Enables adding a preview button in your forms'
long_desc = '''Enables adding a preview button in your forms. See doc for more info.'''

web = 'http://forge.secondweb.fr/%s' % distname


from os import listdir as _listdir
from os.path import join, isdir, exists
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
for dname in ('entities', 'views', 'sobjects', 'hooks', 'schema', 'data', 'i18n', 'migration'):
    if isdir(dname):
        data_files.append([join(THIS_CUBE_DIR, dname), listdir(dname)])
# Note: here, you'll need to add subdirectories if you want
# them to be included in the debian package

__depends_cubes__ = {}
__depends__ = {'cubicweb': '>= 3.9.4'}
