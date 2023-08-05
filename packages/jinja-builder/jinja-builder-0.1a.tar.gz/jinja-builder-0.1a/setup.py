from distutils.core import setup

setup(
  name = 'jinja-builder',
  version = '0.1a',
  description = (
    'a simple jinja2 based JinjaBuilder class for scons'
    ),

  author = 'Stefan Zimmermann',
  author_email = 'zimmermann.code@googlemail.com',
  url = 'http://bitbucket.org/StefanZimmermann/jinja-builder',

  license = 'LGPLv3',

  packages = ['jinja_builder'],

  classifiers = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'License :: OSI Approved ::'
    ' GNU Library or Lesser General Public License (LGPL)',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Software Development',
    'Topic :: Utilities',
    ],

  keywords = [
    'scons', 'jinja', 'jinja2', 'builder', 'build', 'template', 'macro',
    ],
  )
