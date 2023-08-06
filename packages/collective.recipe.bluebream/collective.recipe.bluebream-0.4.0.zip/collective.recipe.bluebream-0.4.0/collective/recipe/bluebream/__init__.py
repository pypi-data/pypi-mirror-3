# This recipe currently does ``nothing``[1][2][3][4] except require Bluebream packages.
# In the future, it may do ``something``.

# [1] Actually, it installs ``bin/paster``
# [2] And it includes a small WSGI application
# [3] And some ZCML files.
# [4] And it creates ``var/{filestorage, blobstorage}`` if they do not exist

from zc.buildout.easy_install import scripts
from zc.recipe.egg import Egg
import logging, os, pkg_resources

logger = logging.getLogger('collective.recipe.bluebream')

def mkdir(dir):
    if not os.path.exists(dir):
        os.mkdir(dir)
    else:
        logger.debug('%s exists' % dir)

class Recipe(object):
    
    def __init__(self, buildout, name, options):

        # Rip off p.r.zope2instance's Egg magic to support ``eggs`` parameter
        # for develop eggs, etc.
        self.egg = Egg(buildout, options['recipe'], options)
        self.buildout = buildout
        self.options = options

    def install(self):

        # Create var dirs
        var = os.path.join(self.buildout['buildout']['directory'], 'var')
        fs = os.path.join(self.buildout['buildout']['directory'], 'var', 'filestorage')
        bs = os.path.join(self.buildout['buildout']['directory'], 'var', 'blobstorage')
        mkdir(var)
        mkdir(fs)
        mkdir(bs)

        # Generate paster script
        requirements, ws = self.egg.working_set(['collective.recipe.bluebream'])
        return scripts(['PasteScript'], ws,
            self.buildout['buildout']['executable'],
            self.buildout['buildout']['bin-directory'])

    def update(self):
        pass

import zope.app.wsgi

def application_factory(global_conf):
    zope_conf = global_conf['zope_conf']
    return zope.app.wsgi.getWSGIApplication(zope_conf)
