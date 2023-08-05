import os.path
from setuptools import setup, find_packages

def read(*names):
    return open(os.path.join(os.path.dirname(__file__), *names), 'r').read()

setup(name='gocept.runner',
      version='0.6.0',
      description="Create stand alone programs with full ZCA",
      long_description=(
          read('src', 'gocept', 'runner', 'appmain.txt')
          + '\n\n'
          + read('src', 'gocept', 'runner', 'once.txt')
          + '\n\n'
          + read('src', 'gocept', 'runner', 'README.txt')
          + '\n\n'
          + read('src', 'gocept', 'runner', 'transaction.txt')
          + '\n\n'
          + read('CHANGES.txt')
      ),
      # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers = (
          "Topic :: Software Development",
          "Framework :: Zope3",
          "Development Status :: 4 - Beta",
          "Intended Audience :: Developers",
          "License :: OSI Approved",
          "License :: OSI Approved :: Zope Public License",
          "Natural Language :: English",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
      ),
      keywords="zope3 mainloop",
      author="gocept gmbh & co. kg",
      author_email="mail@gocept.com",
      url="",
      license="ZPL 2.1",
      package_dir={'': 'src'},
      packages=find_packages('src'),
      include_package_data=True,
      zip_safe=False,
      namespace_packages=['gocept'],
      install_requires=[
          'ZODB3',
          'decorator',
          'setuptools',
          'transaction',
          'zope.app.appsetup>=3.6.0',
          'zope.app.component',
          'zope.app.server',
          'zope.app.wsgi',
          'zope.publisher',
          'zope.security',
          'zope.testing',
      ],
      extras_require=dict(
          test=[
              'gocept.testing>=1.1',
              'mock',
              'zope.app.appsetup>=3.6.0',
              'zope.app.testing',
              'zope.app.zcmlfiles',
              'zope.securitypolicy',
               ]),
      entry_points = dict(
        console_scripts =
          ['runexample = gocept.runner.example:example'])
     )
