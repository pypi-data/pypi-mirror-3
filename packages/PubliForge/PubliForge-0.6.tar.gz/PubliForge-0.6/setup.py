# $Id: setup.py d5e97e0e6a0d 2012/05/09 21:09:45 patrick $

import os

from setuptools import setup, find_packages, Extension

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid>=1.3',
    'pyramid_beaker>=0.6',
    'pyramid_rpc>=0.3.1',
    'Chameleon>=2.8',
    'WebHelpers>=1.3',
    'colander>=0.9.6',
    'SQLAlchemy>=0.7',
    'psycopg2>=2.4',
    'lxml>=2.3',
    'pycrypto>=2.4',
    'Babel>=0.9.6',
    'Mercurial>=2.1',
    'waitress',
    'pyramid_debugtoolbar>=1.0',
    'WebTest>=1.3',
    'WebError>=0.10',
    ]

setup(name='PubliForge',
      version='0.6',
      description='Online multimedia publishing system',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        'Programming Language :: Python',
        'Framework :: Pylons',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        ],
      author='Patrick PIERRE',
      author_email='patrick.pierre@prismallia.fr',
      url='www.publiforge.org',
      keywords='web wsgi bfg pylons pyramid publiforge',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='publiforge',
      install_requires = requires,
      ext_modules = [
          Extension('publiforge.lib.rsync._librsync',
                    ['publiforge/lib/rsync/_librsync.c'],
                    libraries=['rsync'])
          ],
      message_extractors = { '.': [
             ('**.py', 'python', None),
             ('**.pt', 'mako', {'input_encoding': 'utf-8'}),
             ]},
      entry_points = """\
      [paste.app_factory]
      main = publiforge:main
      [console_scripts]
      pfpopulate = publiforge.scripts.pfpopulate:main
      pfbackup = publiforge.scripts.pfbackup:main
      pfbuild = publiforge.scripts.pfbuild:main
      """,
      )
