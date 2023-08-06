from setuptools import find_packages
from setuptools import setup
import os


setup(
    author='Alex Clark',
    author_email='aclark@aclark.net',
    description='collective.recipe.bluebream is a zc.buildout recipe \
        you can use to bootstrap a Bluebream project',
    entry_points={
        'paste.app_factory':
            'main = collective.recipe.bluebream:application_factory',
        'zc.buildout': 'default = collective.recipe.bluebream:Recipe',
    },
    include_package_data=True,
    install_requires=[
        'setuptools',
        'Paste',
        'PasteDeploy',
        'PasteScript',
        'zc.recipe.egg',
        'zope.securitypolicy',
        'zope.component',
        'zope.annotation',
        'zope.browserresource',
        'zope.app.dependable',
        'zope.app.appsetup',
        'zope.app.content',
        'zope.publisher',
        'zope.app.broken',
        'zope.app.component',
        'zope.app.generations',
        'zope.app.error',
        'zope.app.publisher',
        'zope.app.security',
        'zope.app.form',
        'zope.app.i18n',
        'zope.app.locales',
        'zope.app.zopeappgenerations',
        'zope.app.principalannotation',
        'zope.app.basicskin',
        'zope.app.rotterdam',
        'zope.app.folder',
        'zope.app.wsgi',
        'zope.formlib',
        'zope.i18n',
        'zope.app.pagetemplate',
        'zope.app.schema',
        'zope.app.container',
        'zope.app.debug',
        'z3c.evalexception>=2.0',
        'z3c.testsetup',
        'zope.app.testing',
        'zope.testbrowser',
        'zope.login',
        'zope.keyreference',
        'zope.intid',
        'zope.contentprovider',
        'zope.app.zcmlfiles',
    ],
    license='ZPL',
    long_description=(
        open('README.rst').read() +
        open(os.path.join('docs', 'HISTORY.txt')).read()
    ),
    name='collective.recipe.bluebream',
    namespace_packages=[
        'collective',
        'collective.recipe',
    ],
    packages=find_packages(),
    url='https://github.com/collective/collective.recipe.bluebream',
    version='0.4.0',
)
