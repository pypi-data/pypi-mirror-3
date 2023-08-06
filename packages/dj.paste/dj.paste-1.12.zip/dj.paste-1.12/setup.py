from setuptools import setup, find_packages
import os

version = '1.12'

def read(*rnames):
    setupdir =  os.path.dirname( os.path.abspath(__file__))
    return open(
        os.path.join(setupdir, *rnames)
    ).read()

p = os.path.dirname(__file__)
README =read(p,'README.rst')
CHANGELOG  = read(p, 'docs', 'HISTORY.txt')
TESTS  = read(p, 'src', 'dj', 'paste', 'README.txt')

long_description = '%s' % (
    README
    + '\n'
    + TESTS
    + '\n'
    + CHANGELOG
    +'\n'
)
setup(name='dj.paste',
      version=version,
      description="Yet another WSGI Paste factory for paste sponsored by Makina Corpus",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Mathieu Pasquet',
      author_email='kiorky@cryptelium.net',
      url='https://github.com/kiorky/dj.paste',
      license='BSD',
      namespace_packages=['dj', 'dj.paste'],
      include_package_data=True,
      zip_safe=False,
      packages=find_packages('src'),
      extras_require={'test': ['ipython', 'zope.testing', ]},
      package_dir = {'': 'src'},
      install_requires=[
          #'setuptools',
          "WebError",
          'WebOb',
          'PasteScript',
          'Django',
      ],
      entry_points={
          'paste.app_factory': ['main=dj.paste.paste:django_factory',
                                'multi=dj.paste.paste:multi_django_factory', 

                                'mono=dj.paste.paste:django_factory', 
                               ],
          'paste.filter_factory': ['debug=dj.paste.paste:debug_factory',
                                   'weberror=mobyle2.core.webserver:weberror_wrapper' ,
                                  ]
      },
     )
