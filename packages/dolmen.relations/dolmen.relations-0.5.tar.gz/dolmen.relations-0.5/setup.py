# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from os.path import join

name = 'dolmen.relations'
version = '0.5'

readme = open(join('src', 'dolmen', 'relations', 'README.txt')).read()
history = open(join('docs', 'HISTORY.txt')).read()

install_requires = [
    'grokcore.component',
    'setuptools',
    'zc.relation>=1.0',
    'zope.component',
    'zope.container',
    'zope.event',
    'zope.i18nmessageid',
    'zope.interface',
    'zope.intid',
    'zope.lifecycleevent',
    'zope.schema',
    ]

tests_require = [
    'ZODB3>=3.9.1',
    'transaction',
    'zope.testing',
    'zope.keyreference',
    'zope.app.testing',
    'zope.app.zcmlfiles',
    ]

setup(name = name,
      version = version,
      description = 'Dolmen relations',
      long_description = readme + '\n\n' + history,
      keywords = 'Grok Zope3 CMS Dolmen Relations',
      author = 'Souheil Chelfouh',
      author_email = 'trollfot@gmail.com',
      url = 'http://gitweb.dolmen-project.org',
      download_url = '',
      license = 'GPL',
      packages=find_packages('src', exclude=['ez_setup']),
      package_dir={'': 'src'},
      namespace_packages = ['dolmen'],
      include_package_data = True,
      platforms = 'Any',
      zip_safe = False,
      tests_require = tests_require,
      install_requires = install_requires,
      extras_require = {'test': tests_require},
      test_suite="dolmen.relations",
      classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Zope3',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
      ],
)
