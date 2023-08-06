
from distutils.core import setup


setup(
  name = 'wiki2csv',
  version = '1.0',
  scripts = ['wiki2csv.py'],
  author = 'Jan Kanis',
  author_email = 'jan.code@jankanis.nl',
  url = 'http://bitbucket.org/JanKanis/wiki2csv',
  description = 'convert wikipedia tables to csv and back for editing in Excel/LibreOffice',
  long_description = '''Wiki2csv is a command line tool to convert a file containing a table in wikipedia's `wikitable syntax <http://en.wikipedia.org/wiki/Help:Wikitable>`_ to comma separated value syntax and the other way around. It was designed to allow editing of large wikipedia tables using the easier interface of common spreadsheet programs such as Microsoft Excel or `LibreOffice <http://www.libreoffice.org/>`_. Therefore it tries to preserve as much of the layout and formatting directives from the wikitable as possible, and it tries to be fully round trippable.''',
  classifiers = [
    'Programming Language :: Python :: 2.7',
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
    'Operating System :: OS Independent',
    'Topic :: Internet',
    'Topic :: Text Processing :: Markup',
    'Topic :: Utilities',
  ],
)
